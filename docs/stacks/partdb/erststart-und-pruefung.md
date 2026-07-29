# Part-DB-Stack: Erststart und Prüfung

Dieses Dokument beschreibt den ersten Start einer neuen Part-DB-Installation.

Vorher müssen vollständig abgeschlossen sein:

- [Vorbereiten](vorbereiten.md)
- [Authentik einrichten](authentik-einrichten.md)

Insbesondere müssen `.env`, alle sechs Secret-Dateien, DNS, der Core-Stack und beide Authentik-Anwendungen vorhanden sein.

## 1. Images laden

```bash
cd <PROJEKT_ROOT>/Compose/partdb

docker compose pull
```

Dadurch werden die in `.env` gewählten Versionslinien geladen. Die laufenden Core-Container werden nicht verändert.

## 2. Konfiguration vor dem Start prüfen

```bash
docker compose config --quiet
```

Erwartet: keine Ausgabe und Exit-Code `0`.

Zusätzlich alle benötigten lokalen Dateien prüfen:

```bash
for file in \
  .env \
  secrets/partdb_app_secret \
  secrets/mariadb_password \
  secrets/mariadb_root_password \
  secrets/authentik_saml_idp_certificate \
  secrets/partdb_saml_sp_certificate \
  secrets/partdb_saml_sp_private_key
do
  test -s "$file" \
    || { echo "Fehlt oder leer: $file" >&2; exit 1; }
done
```

## 3. Aufgelöste Kernwerte kontrollieren

```bash
docker compose config \
  | grep -E 'image:|partdb\.|partdb_internal|source:|target:'
```

Zu erwarten sind unter anderem:

```text
jbtronics/part-db1:2.14
mariadb:12.3
partdb.<DOMAIN>
partdb_internal
```

Die Ausgabe enthält die **tatsächliche** Domain aus `.env`, nicht den Platzhalter `<DOMAIN>`.

Wichtig:

- Part-DB besitzt kein `ports:`-Mapping.
- MariaDB besitzt kein `ports:`-Mapping.
- `web` ist extern.
- `partdb_internal` ist intern.

## 4. Stack starten

```bash
docker compose up -d
```

Status beobachten:

```bash
watch -n 2 docker compose ps
```

Mit `Ctrl+C` beenden.

Erwarteter stabiler Zustand:

```text
partdb-mariadb   ...   healthy
partdb-server    ...   Up
```

Part-DB besitzt in diesem Stack keinen eigenen Docker-Healthcheck. Deshalb ist für `partdb-server` **`Up`** korrekt; `healthy` darf dort nicht erwartet werden.

## 5. Erstinitialisierung und Migrationen beobachten

```bash
docker compose logs --tail=250 mariadb
docker compose logs --tail=300 partdb
```

Beim ersten Start passiert unter anderem:

1. MariaDB initialisiert das leere Datenverzeichnis.
2. Datenbank und normaler Datenbankbenutzer werden anhand der lokalen Secrets angelegt.
3. Part-DB erkennt eine leere beziehungsweise veraltete Datenbank.
4. Wegen `DB_AUTOMIGRATE=true` werden die erforderlichen Migrationen automatisch ausgeführt.
5. Bei einer neuen Datenbank wird ein lokaler Administrator angelegt.

Eine frühe Meldung, dass Migrationen fehlen beziehungsweise die Datenbank nicht aktuell ist, kann unmittelbar **vor** der automatischen Migration erscheinen. Entscheidend ist, dass die Migration anschließend erfolgreich abgeschlossen wird und der Container nicht in einer Neustartschleife bleibt.

`DB_AUTOMIGRATE` wird von Part-DB als experimentell bezeichnet. Das bei Migrationen unter `uploads/.automigration-backup` angelegte Backup ersetzt kein reguläres externes Backup.

## 6. Initiales Administratorpasswort sofort ersetzen

Bei einer leeren Installation kann Part-DB das zufällig erzeugte Initialpasswort des lokalen Benutzers `admin` in den Startlogs ausgeben. Diese Ausgabe ist ein Secret und darf nicht in Git, Tickets oder öffentliche Diagnoseausgaben kopiert werden.

Unabhängig davon wird jetzt ein eigenes starkes Passwort gesetzt:

```bash
docker compose exec partdb \
  /partdb-secret-entrypoint.sh \
  console partdb:users:set-password admin
```

Die Passworteingabe erfolgt interaktiv.

Das neue Passwort sicher im Passwortmanager speichern. Der lokale `admin` bleibt bewusst als Notfallzugang erhalten.

## 7. MariaDB-Healthcheck manuell prüfen

```bash
docker compose exec mariadb \
  healthcheck.sh \
  --connect \
  --innodb_initialized
```

Erwartet: Exit-Code `0`.

Zusätzlich:

```bash
docker inspect partdb-mariadb \
  --format '{{json .State.Health}}'
```

Erwartet sind mindestens:

```text
"Status":"healthy"
"FailingStreak":0
```

## 8. Netzwerke prüfen

```bash
docker network inspect web
docker network inspect partdb_internal
```

Erwartet:

### `web`

Mindestens:

```text
core-traefik
core-authentik-server
partdb-server
```

`partdb-mariadb` darf dort nicht erscheinen.

### `partdb_internal`

```text
partdb-server
partdb-mariadb
```

## 9. Host-Ports prüfen

```bash
docker compose ps
sudo ss -lntp | grep -E ':(80|443|3306)\s' || true
```

Erwartet:

- TCP 80 und 443 werden weiterhin nur über Docker/Traefik veröffentlicht.
- TCP 3306 ist **nicht** als Host-Port veröffentlicht.
- Bei Part-DB kann `80/tcp` angezeigt werden. Das ist nur der interne Containerport und kein Host-Portmapping.

## 10. HTTP und TLS prüfen

HTTP:

```bash
curl -I http://partdb.<DOMAIN>
```

Erwartet:

```text
301 oder 308
Location: https://partdb.<DOMAIN>/...
```

Bei Produktionszertifikaten:

```bash
curl -I https://partdb.<DOMAIN>/
```

Bei noch aktivem Staging:

```bash
curl -k -I https://partdb.<DOMAIN>/
```

Ohne Authentik-Browsersitzung ist eine Weiterleitung zu `auth.<DOMAIN>` erwartet. Ein direkt ausgelieferter Part-DB-Inhalt wäre in diesem Sicherheitsmodell falsch.

## 11. Outpost-Pfad prüfen

Der Outpost-Pfad wird durch die Router-Labels dieses Stacks bereitgestellt. Er verwendet den Authentik-Service aus dem Core-Stack und darf nicht durch die Forward-Auth-Middleware geschützt werden.

Bei Produktion:

```bash
curl -I \
  https://partdb.<DOMAIN>/outpost.goauthentik.io/ping
```

Bei Staging:

```bash
curl -k -I \
  https://partdb.<DOMAIN>/outpost.goauthentik.io/ping
```

Erwartet:

```text
HTTP/2 204
```

Dieser Pfad wird direkt an Authentik geleitet und darf nicht erneut durch Forward Auth geschützt werden.

## 12. Äußeren Zugriff im privaten Browser testen

In einem privaten Browserfenster öffnen:

```text
https://partdb.<DOMAIN>/
```

Erwarteter Ablauf:

1. Weiterleitung zu Authentik.
2. Authentik-Anmeldung mit einem Benutzer aus einer der `partdb-*`-Gruppen.
3. Rückleitung zu `partdb.<DOMAIN>`.
4. Erst jetzt erscheint die Part-DB-Anmeldeseite beziehungsweise Part-DB-Oberfläche.

Negativtest:

- nicht bei Authentik angemeldet → kein lesbarer Part-DB-Inhalt,
- Authentik-Benutzer ohne `partdb-admin`, `partdb-editor` oder `partdb-readonly` → Zugriff wird durch Authentik verweigert.

## 13. Zuerst lokal als `admin` anmelden

Jetzt **noch nicht** den SAML-Login für den ersten Benutzer verwenden. Das aktuelle `.env`-Mapping ist absichtlich nur:

```dotenv
PARTDB_SAML_ROLE_MAPPING={"*":-1}
```

Nach der Authentik-Forward-Auth-Anmeldung innerhalb von Part-DB mit dem lokalen Benutzer anmelden:

```text
Benutzer: admin
Passwort: das in Schritt 6 gesetzte Passwort
```

## 14. Tatsächliche Part-DB-Gruppen-IDs ermitteln

In Part-DB als lokaler Administrator:

```text
System → Groups / Gruppen
```

Die Gruppen für diese drei Berechtigungsstufen öffnen und im jeweiligen Info-Bereich die numerische ID notieren:

```text
Administratorengruppe
normale schreibende Benutzergruppe
Read-only-Gruppe
```

Die angezeigten Namen und IDs der Installation sind maßgeblich. **Keine IDs aus einer anderen Installation übernehmen.**

Für die folgenden Schritte gelten die Platzhalter:

```text
<PARTDB_ADMIN_GRUPPEN_ID>
<PARTDB_EDITOR_GRUPPEN_ID>
<PARTDB_READONLY_GRUPPEN_ID>
```

## 15. SAML-Gruppenmapping in `.env` fertigstellen

Auf dem Server:

```bash
cd <PROJEKT_ROOT>/Compose/partdb
nano .env
```

Den Übergangswert ersetzen durch:

```dotenv
PARTDB_SAML_ROLE_MAPPING={"partdb-admin":<PARTDB_ADMIN_GRUPPEN_ID>,"partdb-editor":<PARTDB_EDITOR_GRUPPEN_ID>,"partdb-readonly":<PARTDB_READONLY_GRUPPEN_ID>,"*":-1}
```

Die Reihenfolge ist absichtlich:

1. Administrator,
2. Editor,
3. Read-only,
4. Fallback.

Part-DB verwendet beim SAML-Rollenmapping den **ersten passenden Eintrag**. Benutzer mit mehreren Authentik-Gruppen erhalten damit die höher priorisierte vorgesehene Part-DB-Gruppe.

`*:-1` verhindert, dass ein unerwarteter, nicht gemappter SAML-Rollenwert automatisch einer lokalen Gruppe zugeordnet wird.

Konfiguration prüfen und nur Part-DB neu erstellen:

```bash
docker compose config --quiet
docker compose up -d --force-recreate partdb
```

MariaDB muss dafür nicht neu erstellt werden.

## 16. Anonymen Part-DB-Zugriff einschränken

Als lokaler Administrator den speziellen Benutzer `anonymous` öffnen.

Für dieses Projekt gilt:

- alle Berechtigungen auf **verboten** setzen,
- den Benutzer beziehungsweise seine Anmeldung deaktivieren, soweit die verwendete Part-DB-Version diese Option für `anonymous` anbietet.

Part-DB vergibt standardmäßig Leserechte an den anonymen Benutzer. Die zusätzliche Einschränkung sorgt dafür, dass auch nach erfolgreicher äußerer Authentik-Anmeldung keine Part-DB-Daten ohne eigentliche Part-DB-Anmeldung lesbar sind.

Danach abmelden und kontrollieren, dass innerhalb von Part-DB ohne Benutzeranmeldung keine Bestandsdaten lesbar sind.

## 17. SAML-Anmeldung testen

Jetzt die SAML-Anmeldung in Part-DB verwenden.

Mit einem Authentik-Benutzer aus `partdb-admin` testen.

Erwartet:

1. Weiterleitung zum Authentik-SAML-Provider.
2. Wegen vorhandener Authentik-Sitzung normalerweise keine zweite Passwortabfrage.
3. Rückleitung an `https://partdb.<DOMAIN>/saml/acs`.
4. Part-DB erzeugt beim ersten Login einen SAML-Benutzer.
5. Der Benutzer landet durch das Mapping in der vorgesehenen lokalen Administratorengruppe.

Danach nach Möglichkeit zusätzlich je einen Benutzer für `partdb-editor` und `partdb-readonly` testen und die effektiven Rechte kontrollieren.

Der ursprüngliche lokale Benutzer `admin` wird **nicht** in einen SAML-Benutzer umgewandelt.

## 18. PHP-Workaround prüfen

```bash
docker compose exec partdb \
  php -i \
  | grep '^max_input_vars'
```

Erwartet sinngemäß:

```text
max_input_vars => 10000 => 10000
```

Damit ist die versionierte `zz-partdb.ini` sowohl im Container vorhanden als auch für PHP-CLI wirksam. Die gleiche Datei wird zusätzlich für PHP-FPM eingebunden.

## 19. Abschließende Prüfung

```bash
docker compose ps
docker compose logs --since=15m partdb
docker compose logs --since=15m mariadb
```

Die Einrichtung ist abgeschlossen, wenn:

- MariaDB `healthy` ist,
- Part-DB dauerhaft `Up` bleibt,
- keine wiederkehrenden Migrations- oder Datenbankfehler auftreten,
- ohne Authentik-Anmeldung kein Part-DB-Inhalt sichtbar ist,
- ein unberechtigter Authentik-Benutzer am äußeren Zugriff scheitert,
- der lokale Notfalladministrator funktioniert,
- SAML für die vorgesehenen Gruppen funktioniert,
- anonyme Part-DB-Rechte eingeschränkt sind,
- `max_input_vars` den Wert `10000` verwendet,
- MariaDB keinen Host-Port besitzt.

Für den normalen Betrieb weiter mit:

- [Verwaltung und Anwendungseinstellungen](verwaltung.md)
- [Betrieb](betrieb.md)

## Offizielle Referenzen

- [Part-DB: Docker-Installation](https://docs.part-db.de/installation/installation_docker.html)
- [Part-DB: SAML SSO](https://docs.part-db.de/installation/saml_sso.html)
- [Part-DB: Getting started](https://docs.part-db.de/usage/getting_started.html)
- [Part-DB: Console commands](https://docs.part-db.de/usage/console_commands.html)
- [MariaDB Docker Official Image: Healthcheck](https://mariadb.com/kb/en/using-healthcheck-sh/)
