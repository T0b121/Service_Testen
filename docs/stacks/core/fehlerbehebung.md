# Core-Stack: Fehlerbehebung

## 1. Standarddiagnose

```bash
cd <PROJEKT_ROOT>/Compose/core

docker compose config --quiet
docker compose ps -a
docker compose logs --tail=200
docker network inspect web
docker network inspect core_auth
docker volume ls | grep core_
```

## 2. Compose meldet fehlende Variable

```text
The ... variable is not set
```

Prüfen:

```bash
ls -la .env
docker compose config
```

Erwartet: `.env` ist vorhanden, hat idealerweise Modus `600`, und `docker compose config` enthält keine Meldung über nicht gesetzte Variablen. Der Befehl muss im Verzeichnis mit `compose.yml` und `.env` ausgeführt werden.

## 3. `docker compose config --environment` unbekannt

Einige Compose-Versionen unterstützen diese Option nicht.

Verwenden:

```bash
docker compose config
docker compose config --quiet
```

Gezielt filtern:

```bash
docker compose config \
  | grep -E 'acme\.(storage|caserver)'
```

Während des Erstaufbaus erwartet:

```text
--certificatesresolvers.letsencrypt.acme.storage=/acme/acme.json
--certificatesresolvers.letsencrypt.acme.caserver=https://acme-staging-v02.api.letsencrypt.org/directory
```

## 4. Netzwerk `web` fehlt

```text
network web declared as external, but could not be found
```

Lösung:

```bash
docker network create web
docker compose up -d
```

## 5. PostgreSQL unhealthy

```bash
docker compose logs --tail=200 postgresql
docker inspect core-postgresql \
  --format '{{json .State.Health}}'
```

Prüfen:

- Secret-Datei existiert.
- Secret-Datei ist lesbar.
- Volume besitzt genügend Speicher.
- Datenverzeichnis passt zur PostgreSQL-Hauptversion.
- Passwort wurde nicht nachträglich blind ersetzt.

## 6. Authentik Server oder Worker unhealthy

```bash
docker compose logs --tail=200 authentik-server
docker compose logs --tail=200 authentik-worker
docker compose logs --tail=200 postgresql
```

Beim Erststart zunächst Migrationen abwarten.

Dauerhafte Fehler über fehlende Tabellen sind nicht normal.

## 7. Vorübergehende Worker-Fehler bei Erststart

Während Migrationen kann der Worker kurz auf noch nicht vorhandene Tabellen treffen.

Abwarten und danach prüfen:

```bash
docker compose ps
docker compose logs --since=10m authentik-worker
```

Alle Dienste müssen anschließend healthy sein.

## 8. Traefik unhealthy: Ping nicht aktiviert

Fehler:

```text
Error calling healthcheck:
please enable `ping` to use health check
```

Prüfen, ob der Docker-Healthcheck die Parameter enthält:

```bash
docker inspect core-traefik \
  --format '{{json .Config.Healthcheck}}'
```

Korrekte manuelle Prüfung:

```bash
docker exec core-traefik \
  traefik healthcheck \
  --ping=true \
  --ping.entrypoint=ping \
  --entrypoints.ping.address=:8082
```

Erwartet für den vollständigen Aufruf:

```text
OK: http://:8082/ping
```

Der kurze Aufruf ohne Parameter darf in dieser Konfiguration fehlschlagen.

## 9. Authentik liefert 404 oder 502

Router prüfen:

```bash
docker inspect core-authentik-server \
  --format '{{range $key, $value := .Config.Labels}}{{println $key "=" $value}}{{end}}' \
  | sort
```

Netzwerk:

```bash
docker network inspect web
```

Traefik-Logs:

```bash
docker compose logs --since=15m traefik \
  | grep -Ei 'authentik|404|502|error|router'
```

## 10. Initial Setup nicht erreichbar

Vollständige URL:

```text
https://auth.<DOMAIN>/if/flow/initial-setup/
```

Der abschließende Slash ist wichtig.

Container:

```bash
docker compose ps
```

Fallback zum Passwortsetzen:

```bash
docker compose exec \
  authentik-server \
  ak changepassword akadmin
```

## 11. Dashboard liefert 404

Korrekte Adresse:

```text
https://proxy.<DOMAIN>/dashboard/
```

Die Root-Adresse darf 404 liefern:

```text
https://proxy.<DOMAIN>/
```

Dashboard-Labels:

```bash
docker inspect core-traefik \
  --format '{{range $key, $value := .Config.Labels}}{{println $key "=" $value}}{{end}}' \
  | grep traefik-dashboard
```

## 12. Callback liefert 404

Traefik-Logs zeigen beispielsweise:

```text
/outpost.goauthentik.io/callback ... 404
```

Outpost-Router prüfen:

```bash
docker inspect core-authentik-server \
  --format '{{range $key, $value := .Config.Labels}}{{println $key "=" $value}}{{end}}' \
  | grep authentik-outpost
```

Erforderlich:

- Host `proxy.<DOMAIN>`
- Pfad `/outpost.goauthentik.io/`
- Service `authentik`
- Priorität `100`
- keine Forward-Auth-Middleware

Nach Änderung:

```bash
docker compose config --quiet
docker compose up -d --force-recreate authentik-server
```

## 13. Embedded Outpost funktioniert nicht

Prüfen:

```bash
curl -k -I \
  https://auth.<DOMAIN>/outpost.goauthentik.io/ping
```

Erwartet:

```text
204
```

In Authentik:

- Embedded Outpost gesund?
- Anwendung ausgewählt?
- Provider konfiguriert?
- richtige externe URL?

## 14. Endlosschleife bei Anmeldung

Prüfen:

- externe Provider-URL exakt `https://proxy.<DOMAIN>`
- Browsercookies
- Uhrzeit des Servers
- Callback-Router
- kein Forward Auth auf dem Outpost-Router
- kein alter Provider mit abweichender Domain

Privates Browserfenster verwenden.

## 15. Administrator erhält keinen Zugriff

In Authentik:

- Benutzer Mitglied von `authentik Admins`?
- Binding aktiv?
- `Negate` deaktiviert?
- Failure Result korrekt?
- Zugangsprüfung ausführen.
- Für einen Negativtest einen `Internal User` verwenden, der nicht Mitglied von `authentik Admins` ist; siehe [Authentik verwalten](authentik-verwaltung.md#internen-benutzer-oder-testbenutzer-anlegen).

## 16. Technischer Outpost-Benutzer wird abgelehnt

Ein Konto mit Namen `ak-outpost-...` muss die Admin-Gruppenbindung nicht bestehen. Das ist normal.

## 17. Große Uploads

```text
maxResponseBodySize=1048576
```

begrenzt nur die Antwort des Authentifizierungsservers. Es begrenzt keinen Video- oder Cloud-Upload.

Bei Uploadproblemen stattdessen prüfen:

- Anwendungslimit
- zusätzliche Traefik-Buffering-Middleware
- Timeouts
- Proxy- oder CDN-Limits
- freier Speicher
- Webserverlimit des Zielstacks

## 18. Staging-Zertifikat nicht vertrauenswürdig

Das ist während der Einrichtung erwartet.

Aktiven CA-Server prüfen:

```bash
docker compose config \
  | grep 'acme.caserver'
```

Während der Einrichtung erwartet:

```text
https://acme-staging-v02.api.letsencrypt.org/directory
```

Produktionswechsel nur nach der Anleitung:

- [TLS und Zertifikate](../../tls-und-zertifikate.md)

## 19. ACME-Challenge fehlschlägt

```bash
docker compose logs traefik \
  | grep -Ei 'acme|challenge|certificate|error'
```

Prüfen:

- A-Eintrag
- AAAA-Eintrag
- Port 80
- Firewall
- anderer Webserver
- Providerfirewall
- Domain bereits auf anderen Server gerichtet

## 20. Labels wurden nicht übernommen

Aufgelöste Konfiguration:

```bash
docker compose config
```

Container neu erstellen:

```bash
docker compose up -d --force-recreate \
  traefik \
  authentik-server
```

Danach mit `docker inspect` prüfen.

## 21. Leere Neuinstallation trotz alter Erwartung

Volumes prüfen:

```bash
docker volume ls | grep core_
docker compose config \
  | grep -A3 -E 'postgresql_data:|authentik_data:'
```

Häufige Ursachen:

- Volume gelöscht
- Volume-Name geändert
- `.env` nicht geladen
- anderes Compose-Projekt
- `docker compose down -v`

Neue Secrets oder leere Volumes stellen keine alten Daten wieder her.

## 22. Worker erreicht externe Dienste nicht

Der Worker hängt beabsichtigt nur im internen Netzwerk `core_auth`.

Für SMTP, Webhooks oder externe Synchronisierung ist ein separates Egress-Netzwerk erforderlich. Siehe:

- [Authentik verwalten](authentik-verwaltung.md#netzwerk-für-e-mail-und-externe-aufgaben)
