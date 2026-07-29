# Part-DB-Stack: Fehlerbehebung

## 1. Standarddiagnose

```bash
cd <PROJEKT_ROOT>/Compose/partdb

docker compose config --quiet
docker compose ps -a
docker compose logs --tail=250
docker network inspect web
docker network inspect partdb_internal
docker volume ls | grep partdb_
```

Bei einem Web-/SSO-Problem zusätzlich den Core-Stack prüfen:

```bash
cd <PROJEKT_ROOT>/Compose/core
docker compose ps
docker compose logs --tail=150 traefik authentik-server
```

## 2. Compose meldet fehlende Variable

Beispiel:

```text
The ... variable is not set
```

Prüfen:

```bash
cd <PROJEKT_ROOT>/Compose/partdb
ls -la .env
docker compose config
```

Die `.env` muss direkt neben `compose.yml` liegen und alle Werte aus [Vorbereiten](vorbereiten.md) enthalten.

## 3. Wrapper meldet fehlenden Konfigurationswert

Beispiel:

```text
DOMAIN ist nicht gesetzt
PARTDB_SAML_ROLE_MAPPING ist nicht gesetzt
```

Der eigene Entrypoint prüft die zwingend benötigten Werte beim Start.

Prüfen:

```bash
grep -E '^(DOMAIN|PARTDB_|MARIADB_)' .env
```

Dabei stehen in der aktuellen `.env` keine Passwörter; die Ausgabe darf trotzdem nicht unnötig öffentlich geteilt werden.

Nach Korrektur:

```bash
docker compose config --quiet
docker compose up -d --force-recreate partdb
```

## 4. Wrapper meldet Secret nicht lesbar oder leer

Beispiel:

```text
Fehler: Secret '...' ist nicht lesbar
Fehler: Secret '...' ist leer
```

Prüfen, ohne Inhalte auszugeben:

```bash
for file in secrets/*; do
  stat -c '%A %s Bytes %n' "$file"
done
```

Erforderlich sind:

```text
partdb_app_secret
mariadb_password
mariadb_root_password
authentik_saml_idp_certificate
partdb_saml_sp_certificate
partdb_saml_sp_private_key
```

Leere oder fehlende Dateien nach der jeweiligen Einrichtungsanleitung wiederherstellen. Bestehende Secrets nicht blind neu generieren.

## 5. Netzwerk `web` fehlt

Fehler:

```text
network web declared as external, but could not be found
```

Der Core-Aufbau muss das externe Netzwerk bereits erzeugt haben.

Prüfen:

```bash
docker network inspect web
```

Falls das System neu aufgebaut wird und das Netzwerk tatsächlich fehlt:

```bash
docker network create web
```

Danach Core zuerst prüfen und erst anschließend Part-DB starten.

## 6. MariaDB ist `unhealthy`

```bash
docker compose logs --tail=250 mariadb

docker inspect partdb-mariadb \
  --format '{{json .State.Health}}'
```

Prüfen:

- `mariadb_password` und `mariadb_root_password` vorhanden,
- genügend freier Speicher,
- `partdb_mariadb_data` vorhanden,
- Image-Version mit dem vorhandenen Datenverzeichnis kompatibel,
- kein blind geändertes Datenbankpasswort.

Manueller Healthcheck:

```bash
docker compose exec mariadb \
  healthcheck.sh \
  --connect \
  --innodb_initialized
```

## 7. Part-DB startet immer neu

```bash
docker compose ps -a
docker compose logs --tail=300 partdb
```

Typische Ursachen:

- fehlendes Secret,
- ungültige `.env`,
- MariaDB nicht erreichbar,
- fehlerhaftes SAML-Zertifikatsformat,
- Datenbankmigration fehlgeschlagen,
- inkompatibles Image nach Update.

Nicht als ersten Schritt Volumes löschen.

## 8. Meldung über ausstehende Migrationen beim Erststart

`DB_AUTOMIGRATE=true` ist aktiv. Beim Start kann Part-DB zunächst erkennen, dass Migrationen fehlen, und sie anschließend automatisch ausführen.

Logs weiter beobachten:

```bash
docker compose logs -f partdb
```

Ein einmaliger Vorabhinweis ist vom dauerhaft fehlgeschlagenen Migrationslauf zu unterscheiden.

Wenn der Container wiederholt scheitert, keine Migration blind erneut erzwingen. Zuerst Backupzustand, Datenbanklogs und konkrete Fehlermeldung prüfen.

## 9. Initiales Adminpasswort nicht mehr bekannt

Neues Passwort setzen:

```bash
docker compose exec partdb \
  /partdb-secret-entrypoint.sh \
  console partdb:users:set-password admin
```

Keine alten Startlogs veröffentlichen, nur um das initial erzeugte Passwort wiederzufinden.

## 10. Part-DB liefert `404` oder `502`

Part-DB-Router prüfen:

```bash
docker inspect partdb-server \
  --format '{{range $key, $value := .Config.Labels}}{{println $key "=" $value}}{{end}}' \
  | sort \
  | grep 'traefik.http'
```

Netzwerk:

```bash
docker network inspect web
```

Core-Traefik-Logs:

```bash
cd <PROJEKT_ROOT>/Compose/core

docker compose logs --since=15m traefik \
  | grep -Ei 'partdb|404|502|error|router'
```

`partdb-server` muss im Netzwerk `web` sein; Traefik verwendet intern Port 80.

## 11. Aufruf leitet zu Authentik weiter

Ohne Authentik-Sitzung ist das **erwartet**.

Prüfung:

```bash
curl -k -I https://partdb.<DOMAIN>/
```

Eine `302`-Weiterleitung zu `auth.<DOMAIN>` zeigt, dass die äußere Forward-Auth-Schicht greift.

Problematisch wäre dagegen ein direktes `200` mit lesbarem Part-DB-Inhalt für einen nicht authentifizierten Client.

## 12. Part-DB-Outpost-Pfad liefert `404`

```bash
curl -k -I \
  https://partdb.<DOMAIN>/outpost.goauthentik.io/ping
```

Erwartet:

```text
HTTP/2 204
```

Part-DB-Labels prüfen:

```bash
docker inspect partdb-server \
  --format '{{range $key, $value := .Config.Labels}}{{println $key "=" $value}}{{end}}' \
  | grep 'authentik-outpost-partdb'
```

Erforderlich sind sinngemäß:

```text
Host partdb.<DOMAIN>
PathPrefix /outpost.goauthentik.io/
service authentik@docker
priority 100
keine Forward-Auth-Middleware auf diesem Router
```

Fehlen diese Labels im aktuellen Git-Stand, ist nicht die Installation manuell anzupassen, sondern zuerst zu prüfen, ob der richtige Repository-Stand verwendet wird.

## 13. Authentik verweigert einem berechtigten Benutzer den äußeren Zugriff

In Authentik prüfen:

- Benutzer in mindestens einer `partdb-*`-Gruppe?
- `Part-DB Access` vorhanden?
- Gruppenbindings aktiv?
- `Policy Engine Mode: ANY`?
- `Part-DB Access` dem Embedded Outpost zugeordnet?
- Zugangsprüfung des Providers erfolgreich?

Ein Benutzer ohne passende Gruppe **soll** abgewiesen werden.

## 14. Endlosschleife oder falsche HTTP/HTTPS-URL

Prüfen:

- `DOMAIN` in `.env`,
- Aufruf wirklich über `https://partdb.<DOMAIN>`,
- Systemzeit,
- Browsercookies beziehungsweise privates Fenster,
- Part-DB-Outpost-Router,
- SAML-Provider-URLs,
- Core-Traefik-Logs.

Der Wrapper setzt automatisch:

```text
DEFAULT_URI=https://partdb.<DOMAIN>/
TRUSTED_HOSTS für partdb.<DOMAIN>
SAML_BEHIND_PROXY=1
```

Diese Werte werden bei normaler Installation nicht manuell in `compose.yml` geändert.

## 15. SAML-Schaltfläche fehlt

Prüfen:

```bash
docker compose logs --tail=200 partdb
```

Und die SAML-Secrets:

```bash
stat -c '%A %s Bytes %n' \
  secrets/authentik_saml_idp_certificate \
  secrets/partdb_saml_sp_certificate \
  secrets/partdb_saml_sp_private_key
```

Der Wrapper setzt `SAML_ENABLED=1`. Fehlt die Schaltfläche trotzdem, zuerst Startfehler beziehungsweise ungültige SAML-Konfiguration untersuchen.

## 16. SAML-Login endet mit Signatur- oder Zertifikatsfehler

Lokales IdP-Zertifikat prüfen:

```bash
base64 -d secrets/authentik_saml_idp_certificate \
  | openssl x509 -inform DER -noout \
      -subject -issuer -dates -fingerprint -sha256
```

In Authentik prüfen:

- `Part-DB SSO` verwendet das erwartete Signing Certificate,
- Verification Certificate ist `Part-DB SAML SP`,
- Sign Assertions aktiviert,
- Sign Responses aktiviert,
- ACS und Audience stimmen exakt.

Wenn Authentiks Signing Certificate rotiert wurde, das IdP-Zertifikatssecret nach [Authentik einrichten](authentik-einrichten.md) aktualisieren und Part-DB neu erstellen.

## 17. SAML-Benutzer landet in falscher Gruppe

In Authentik:

- Property Mapping heißt `Part-DB Gruppen`,
- SAML Attribute Name ist exakt `group`,
- Mapping-Test liefert den vorgesehenen Gruppennamen.

In `.env`:

```bash
grep '^PARTDB_SAML_ROLE_MAPPING=' .env
```

Prüfen:

- tatsächliche lokale Part-DB-Gruppen-IDs,
- Reihenfolge Admin → Editor → Read-only → `*`,
- keine IDs aus einer anderen Installation,
- `*` steht auf `-1`, wenn nicht gemappte Rollen keine Gruppe erhalten sollen.

Nach Änderung:

```bash
docker compose up -d --force-recreate partdb
```

Danach Benutzer neu über SAML anmelden. `SAML_UPDATE_GROUP_ON_LOGIN=true` aktualisiert die Gruppe bei der Anmeldung.

## 18. Lokaler Benutzer kann nicht über SAML angemeldet werden

Part-DB unterscheidet lokale und SAML-Benutzer bewusst. Ein lokaler Benutzer kann nicht einfach mit demselben Konto über SAML authentifiziert werden.

Für den Notfalladministrator `admin` ist das gewollt.

Wenn ein anderer vorhandener lokaler Benutzer bewusst migriert werden soll, die offizielle Part-DB-Anleitung zur Konvertierung von Benutzern verwenden. Nicht den Notfalladministrator konvertieren.

## 19. Ohne Part-DB-Login sind Daten sichtbar

Part-DBs Benutzer `anonymous` prüfen.

Die Defaultkonfiguration von Part-DB kann anonyme Leserechte besitzen. Für dieses Projekt werden Anonymous-Berechtigungen auf verboten gesetzt.

Nach Änderung:

1. von Part-DB abmelden,
2. Authentik-Sitzung kann bestehen bleiben,
3. Part-DB-Seiten erneut aufrufen,
4. kontrollieren, dass Bestandsdaten ohne Part-DB-Sitzung nicht lesbar sind.

Wenn eine bestimmte Part-DB-Version bei vollständig verbotenen Anonymous-Rechten UI-Probleme zeigt, zuerst die Release Notes beziehungsweise aktuelle Part-DB-Issues prüfen, statt Schutzrechte pauschal wieder freizugeben.

## 20. Große Projekte oder Formulare schlagen fehl

PHP-Wert prüfen:

```bash
docker compose exec partdb \
  php -i \
  | grep '^max_input_vars'
```

Erwartet:

```text
max_input_vars => 10000 => 10000
```

Falls weiterhin der PHP-Standardwert erscheint:

```bash
docker inspect partdb-server \
  --format '{{json .Mounts}}'
```

Die versionierte Datei `config/zz-partdb.ini` muss in die FPM- und CLI-`conf.d`-Verzeichnisse eingehängt sein.

## 21. REST-API, KiCad oder MCP funktioniert trotz gültigem Part-DB-Token nicht

In der Basiskonfiguration schützt Authentik Forward Auth auch diese Pfade.

Ein Maschinenclient mit nur einem Part-DB-Bearer-Token kann deshalb bereits an Authentik scheitern.

Das ist aktuell beabsichtigt. Keine breite Ausnahme improvisieren.

Siehe:

- [API, KiCad und MCP](api-kicad-und-mcp.md)

## 22. Informationsanbieter können externe Dienste nicht erreichen

Prüfen:

```bash
docker compose exec partdb \
  getent ahostsv4 github.com
```

Danach Part-DB-Logs und den konkreten Provider prüfen.

Mögliche Ursachen:

- DNS/Egress des Hosts,
- Provider-API nicht erreichbar,
- API-Key oder OAuth-Verbindung fehlt,
- Part-DB-Benutzer besitzt nicht die nötige Providerberechtigung,
- Provider verlangt ausschließlich env-basierte Zugangsdaten, die vom aktuellen Compose-Stack nicht injiziert werden.

Den letzten Punkt nicht durch eine einmalige manuelle Änderung von `compose.yml` lösen. Für env-only Provider ist eine reproduzierbare, versionierte Erweiterung des Stacks erforderlich.

## 23. MariaDB-Passwort wurde in der Secret-Datei geändert

Ein neues `secrets/mariadb_password` ändert nicht automatisch das Passwort des bereits existierenden MariaDB-Benutzers im persistenten Datenbankvolume.

Folgen können sein:

```text
Access denied
Part-DB kann Datenbank nicht erreichen
```

Nicht weiter rotieren. Ursprüngliches Secret aus sicherem Backup wiederherstellen oder eine geplante Passwortrotation durchführen, bei der Datenbankbenutzer und Part-DB-Konfiguration koordiniert geändert werden.

## 24. Staging-Zertifikat wird nicht vertraut

Während der Einrichtung mit Let's Encrypt Staging ist das normal.

Für Tests kann temporär verwendet werden:

```bash
curl -k -I https://partdb.<DOMAIN>/
```

Für normalen Betrieb und Maschinenclients auf Produktion wechseln:

- [TLS und Zertifikate](../../tls-und-zertifikate.md)

## 25. Part-DB oder MariaDB zeigt keinen Host-Port

Das ist **kein Fehler**.

Die Architektur veröffentlicht ausschließlich Traefik auf TCP 80 und 443. Part-DB und MariaDB bleiben hinter Docker-Netzwerken.

`80/tcp` oder `3306/tcp` in einer Containeranzeige können interne Ports darstellen. Ein Host-Portmapping würde als Zuordnung wie `0.0.0.0:PORT->...` erscheinen.

## Offizielle Referenzen

- [Part-DB: Troubleshooting](https://docs.part-db.de/troubleshooting.html)
- [Part-DB: Docker-Installation](https://docs.part-db.de/installation/installation_docker.html)
- [Part-DB: SAML SSO](https://docs.part-db.de/installation/saml_sso.html)
- [Part-DB: Getting started](https://docs.part-db.de/usage/getting_started.html)
- [Authentik: Forward Auth](https://docs.goauthentik.io/add-secure-apps/providers/proxy/forward_auth/)
