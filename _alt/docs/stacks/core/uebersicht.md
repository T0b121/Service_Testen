# Core-Stack: Übersicht

## 1. Zweck

Der Core-Stack stellt gemeinsame Basisdienste bereit:

- Traefik als Reverse Proxy und TLS-Endpunkt
- Authentik als Identitäts-, Authentifizierungs- und Autorisierungsdienst
- Authentik Worker für Hintergrundaufgaben
- PostgreSQL als Authentik-Datenbank

Andere Stacks können später Traefik und Authentik verwenden.

## 2. Vorausgesetzte Stacks

Keine.

Der Core-Stack muss vor Stacks laufen, die:

- über Traefik veröffentlicht werden,
- Authentik als SSO- oder Forward-Auth-Dienst verwenden.

## 3. Dienste

| Compose-Dienst | Container | Aufgabe | Öffentlich |
|---|---|---|---|
| `traefik` | `core-traefik` | Reverse Proxy, TLS, Dashboard | TCP 80 und 443 |
| `authentik-server` | `core-authentik-server` | Weboberfläche, API, eingebetteter Outpost | nur über Traefik |
| `authentik-worker` | `core-authentik-worker` | Hintergrundaufgaben | Nein |
| `postgresql` | `core-postgresql` | Authentik-Datenbank | Nein |

## 4. Öffentliche Endpunkte

| Zweck | Adresse |
|---|---|
| Authentik | `https://auth.<DOMAIN>` |
| Traefik-Dashboard | `https://proxy.<DOMAIN>/dashboard/` |

Die Adresse:

```text
https://proxy.<DOMAIN>/
```

darf absichtlich `404 page not found` liefern.

## 5. Ports

### Am Host veröffentlicht

```text
80/tcp
443/tcp
```

Nur Traefik veröffentlicht Ports.

### Intern

```text
authentik-server:9000
traefik ping:8082
postgresql:5432
```

Port `8082` ist nur der interne Traefik-Healthcheck und wird nicht unter `ports:` veröffentlicht.

## 6. Netzwerke

### `web`

Externes Docker-Netzwerk:

```text
core-traefik
core-authentik-server
```

Zweck:

- Traefik erreicht Authentik.
- spätere Stacks können ihre öffentlichen Frontends mit Traefik verbinden.

### `core_auth`

Internes Netzwerk:

```text
core-postgresql
core-authentik-server
core-authentik-worker
```

Eigenschaft:

```yaml
internal: true
```

Dadurch ist regulärer ausgehender Internetzugriff über dieses Netzwerk blockiert.

## 7. Worker-Isolation

Der Worker hängt ausschließlich in `core_auth`.

Das ist aktuell beabsichtigt:

- keine öffentliche Erreichbarkeit
- kein unnötiges Proxy-Netzwerk
- kein allgemeiner Internet-Egress

Dadurch können spätere Worker-Aufgaben eingeschränkt sein, beispielsweise:

- E-Mail-Versand
- externe Verzeichnissynchronisierung
- Webhooks
- externe Provider
- Updateprüfungen

Falls eine solche Funktion benötigt wird, wird dafür eine versionierte Stack-Erweiterung mit einem separaten, nicht internen Egress-Netzwerk vorgesehen. Der Worker muss dafür nicht an `web` angeschlossen werden.

## 8. Volumes

| Volume | Inhalt |
|---|---|
| `core_postgresql_data` | PostgreSQL-Daten |
| `core_authentik_data` | Authentik-Dateien unter `/data` |
| `core_traefik_acme_staging` | ACME-Staging-Konto und Zertifikate |
| `core_traefik_acme_production` | späteres Produktionskonto und Zertifikate |

Welches ACME-Volume aktiv ist, wird über `TRAEFIK_ACME_VOLUME` in der lokalen `.env` bestimmt.

## 9. Secrets

| Secret-Datei | Verwendet von |
|---|---|
| `secrets/postgresql_password` | PostgreSQL, Authentik Server, Authentik Worker |
| `secrets/authentik_secret_key` | Authentik Server, Authentik Worker |

Sie werden im Container unter `/run/secrets/` eingehängt.

## 10. Abhängigkeiten

```text
PostgreSQL healthy
├── Authentik Server
└── Authentik Worker

Traefik
└── erreicht Authentik Server über web
```

Compose wartet für Authentik Server und Worker auf den PostgreSQL-Healthcheck.

## 11. Healthchecks

| Dienst | Prüfung |
|---|---|
| PostgreSQL | `pg_isready` |
| Authentik Server | integrierter Image-Healthcheck |
| Authentik Worker | integrierter Image-Healthcheck |
| Traefik | interner `/ping`-Endpunkt auf Port 8082 |

Der manuelle Traefik-Test benötigt die statischen Ping-Parameter:

```bash
docker exec core-traefik \
  traefik healthcheck \
  --ping=true \
  --ping.entrypoint=ping \
  --entrypoints.ping.address=:8082
```

## 12. Traefik-Dashboard und Authentik-Outpost-Routen

Dashboard-Router:

```text
Host proxy.<DOMAIN>
Pfade /api und /dashboard
Ziel api@internal
Middleware authentik
```

Für Single-Application-Forward-Auth benötigt jede geschützte Anwendungsdomain einen separaten Outpost-Pfad unter `/outpost.goauthentik.io/`.

### Dashboard-Outpost

```text
Host proxy.<DOMAIN>
Pfad /outpost.goauthentik.io/
Ziel Authentik Server
keine Forward-Auth-Middleware
Priorität 100
```

## 13. Forward-Auth-Antwortgröße

```text
maxResponseBodySize=1048576
```

Dies begrenzt nur die Antwort des Authentifizierungsdienstes auf 1 MiB. Es begrenzt keine späteren Datei-Uploads zu anderen Diensten.

## 14. Zertifikate

Standard während der Einrichtung:

```text
Let’s Encrypt Staging
HTTP-01
```

Details und Produktionswechsel:

- [TLS und Zertifikate](../../tls-und-zertifikate.md)

## 15. Zu sichernde Daten

- `compose.yml`
- `.env`
- beide Secret-Dateien
- PostgreSQL-Dump
- Authentik-Datenvolume
- produktives ACME-Volume
- verwendete Image-Tags

Details:

- [Core: Backup und Wiederherstellung](backup-und-wiederherstellung.md)
