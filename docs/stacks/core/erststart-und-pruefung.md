# Core-Stack: Erststart und Prüfung

Diese Datei beschreibt den ersten Start einer leeren Installation.

Vorher muss [vorbereiten.md](vorbereiten.md) vollständig abgeschlossen sein. Diese Anleitung setzt insbesondere eine ausgefüllte `.env`, erzeugte Secret-Dateien, korrektes DNS, freie Ports und das externe Netzwerk `web` voraus.

Für den normalen Betrieb wird später [betrieb.md](betrieb.md) verwendet. Werden `.env`, Secrets, DNS oder grundlegende Netzwerke geändert, ist erneut die zugehörige Prüfung aus [vorbereiten.md](vorbereiten.md) maßgeblich.

## 1. Images laden

```bash
cd <PROJEKT_ROOT>/Compose/core

docker compose pull
```

## 2. Konfiguration prüfen

```bash
docker compose config --quiet
```

Erwartet: keine Ausgabe und Exit-Code `0`.

Optional vollständige Auflösung:

```bash
docker compose config
```

Erwartete Kernwerte in der aufgelösten Ausgabe:

```text
image: traefik:3.7
image: ghcr.io/goauthentik/server:2026.5
image: postgres:18
--certificatesresolvers.letsencrypt.acme.storage=/acme/acme.json
--certificatesresolvers.letsencrypt.acme.caserver=https://acme-staging-v02.api.letsencrypt.org/directory
name: core_traefik_acme_staging
target: /run/secrets/postgresql_password
target: /run/secrets/authentik_secret_key
```

Außerdem gilt:

- Die Router enthalten die echte Domain und kein wörtliches `<DOMAIN>`.
- Authentik Server und Worker verwenden dasselbe Authentik-Image.
- Nur TCP 80 und 443 sind veröffentlicht.
- Für PostgreSQL, Authentik oder Port 8082 existiert kein Host-Portmapping.
- Compose meldet keine Warnung über nicht gesetzte Variablen. Absichtlich escapte Container-Variablen im PostgreSQL-Healthcheck dürfen in der aufgelösten Ausgabe weiterhin als `$${POSTGRES_DB}` beziehungsweise `$${POSTGRES_USER}` erscheinen.

## 3. Starten

```bash
docker compose up -d
```

Status beobachten:

```bash
watch -n 2 docker compose ps
```

Mit `Ctrl+C` beenden.

Erwartet:

```text
core-postgresql         healthy
core-authentik-server   healthy
core-authentik-worker   healthy
core-traefik            healthy
```

## 4. Erstinitialisierung

Beim ersten Start:

1. PostgreSQL initialisiert das Datenverzeichnis.
2. Authentik führt Datenbankmigrationen aus.
3. der Worker verbindet sich mit PostgreSQL.
4. Traefik registriert das Staging-ACME-Konto.
5. Traefik fordert Staging-Zertifikate an.

Vorübergehende Authentik-Warnungen über noch nicht vorhandene Tabellen können während der Migration auftreten. Sie müssen nach Abschluss verschwinden.

## 5. Logs prüfen

```bash
docker compose logs --tail=150 postgresql
docker compose logs --tail=150 authentik-server
docker compose logs --tail=150 authentik-worker
docker compose logs --tail=150 traefik
```

Fehler filtern:

```bash
docker compose logs --since=15m \
  | grep -Ei 'error|fatal|panic|exception|failed'
```

Erwartet nach abgeschlossener Initialisierung: keine dauerhaft wiederkehrenden Fehler. Einzelne frühe Migrationsmeldungen können im historischen Log stehen; entscheidend sind anschließend gesunde Container und keine fortlaufenden Wiederholungen.

## 6. Healthchecks

### Gesamtstatus

```bash
docker compose ps
```

### Traefik

Der kurze Befehl ohne Parameter:

```bash
docker exec core-traefik traefik healthcheck
```

kann in dieser Konfiguration mit „please enable ping“ fehlschlagen, weil der separat gestartete CLI-Prozess die Startparameter des Hauptprozesses nicht automatisch übernimmt.

Korrekte manuelle Prüfung:

```bash
docker exec core-traefik \
  traefik healthcheck \
  --ping=true \
  --ping.entrypoint=ping \
  --entrypoints.ping.address=:8082
```

Erwartet:

```text
OK: http://:8082/ping
```

Docker-Healthstatus:

```bash
docker inspect core-traefik \
  --format '{{json .State.Health}}'
```

Erwartet sind mindestens:

```text
"Status":"healthy"
"FailingStreak":0
```

## 7. Netzwerke prüfen

```bash
docker network inspect web
docker network inspect core_auth
```

Erwartet:

### `web`

```text
core-traefik
core-authentik-server
```

### `core_auth`

```text
core-postgresql
core-authentik-server
core-authentik-worker
```

## 8. Ports prüfen

```bash
docker compose ps
sudo ss -lntp | grep -E ':(80|443)\s'
```

Erwartet:

- Traefik veröffentlicht `80:80` und `443:443` für IPv4 und gegebenenfalls IPv6.
- Authentik zeigt nur den internen Eintrag `9000/tcp`.
- PostgreSQL und Worker besitzen kein Host-Portmapping.
- Port `8082` erscheint nicht als veröffentlichter Host-Port.

## 9. HTTP-Redirect

```bash
curl -I http://auth.<DOMAIN>
curl -I http://proxy.<DOMAIN>/dashboard/
```

Erwartet:

```text
301 oder 308
Location: https://...
```

## 10. Authentik über HTTPS

Weil Staging aktiv ist:

```bash
curl -k -I https://auth.<DOMAIN>
```

Erwartet ist eine erfolgreiche HTTP-Antwort oder Weiterleitung, typischerweise `200` oder `302`. `404`, `502` oder ein Verbindungsfehler sind nicht erwartbar. Die Browserwarnung wegen des Staging-Zertifikats ist in dieser Phase normal.

## 11. Authentik initial einrichten

Öffnen:

```text
https://auth.<DOMAIN>/if/flow/initial-setup/
```

Bei Authentik 2026.5 kann die Root-Adresse automatisch dorthin weiterleiten.

Wichtig: Der abschließende Slash gehört zur URL.

Jetzt mit folgender Anleitung fortfahren:

- [Authentik einrichten](authentik-einrichten.md)

Danach zu diesem Dokument zurückkehren.

## 12. Outpost prüfen

Nach der Authentik-Einrichtung:

```bash
curl -k -I \
  https://auth.<DOMAIN>/outpost.goauthentik.io/ping
```

Erwartet:

```text
HTTP/2 204
```

## 13. Dashboard prüfen

Im privaten Browserfenster:

```text
https://proxy.<DOMAIN>/dashboard/
```

Erwarteter Ablauf:

1. Weiterleitung zu Authentik
2. Anmeldung
3. Autorisierungsprüfung
4. Callback unter `/outpost.goauthentik.io/`
5. Traefik-Dashboard

Prüfen:

- Administrator erhält Zugriff.
- Benutzer außerhalb `authentik Admins` erhält keinen Zugriff.
- kein Callback-404.
- `https://proxy.<DOMAIN>/` darf weiterhin 404 liefern.

## 14. Router-Labels prüfen

Dashboard:

```bash
docker inspect core-traefik \
  --format '{{range $key, $value := .Config.Labels}}{{println $key "=" $value}}{{end}}' \
  | sort \
  | grep traefik-dashboard
```

Erwartet sind Routerregel, EntryPoint `websecure`, TLS mit Resolver `letsencrypt`, Service `api@internal` und Middleware `authentik`.

Forward Auth:

```bash
docker inspect core-traefik \
  --format '{{range $key, $value := .Config.Labels}}{{println $key "=" $value}}{{end}}' \
  | sort \
  | grep 'middlewares.authentik'
```

Erwartet sind die interne Authentik-Adresse, `trustForwardHeader=true`, die Antwortheader und `maxResponseBodySize=1048576`.

Outpost-Router:

```bash
docker inspect core-authentik-server \
  --format '{{range $key, $value := .Config.Labels}}{{println $key "=" $value}}{{end}}' \
  | sort \
  | grep authentik-outpost
```

Erwartet sind Host `proxy.<DOMAIN>`, Pfad `/outpost.goauthentik.io/`, EntryPoint `websecure`, Service `authentik`, TLS und Priorität `100`. Die Ausgabe darf keine Forward-Auth-Middleware für diesen Router enthalten.

## 15. Abschluss

```bash
docker compose ps
docker compose logs --tail=100
```

Danach:

- normaler Betrieb: [betrieb.md](betrieb.md)
- Produktionszertifikate später: [TLS und Zertifikate](../../tls-und-zertifikate.md)
- Backup: [backup-und-wiederherstellung.md](backup-und-wiederherstellung.md)
