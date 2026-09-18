# Core-Stack vorbereiten

## 1. Voraussetzungen

Vorher abschließen:

- [Server vorbereiten](../../server/vorbereiten.md)
- [Server konfigurieren](../../server/konfigurieren.md)

Benötigt:

- DNS für `auth.<DOMAIN>` und `proxy.<DOMAIN>`
- TCP 80 und 443 frei und erreichbar
- Docker und Compose V2
- externes Docker-Netzwerk `web`
- vorhandene `compose.yml`

## 2. Verzeichnis

```bash
cd <PROJEKT_ROOT>
mkdir -p Compose/core/secrets
cd Compose/core
```

Erwartet zu diesem Zeitpunkt:

```text
Compose/core/
├── compose.yml
└── secrets/
```

Das Verzeichnis `secrets/` ist noch leer. Die `.env` wird in Schritt 3 erstellt; die beiden Secret-Dateien werden erst in Schritt 4 erzeugt.

## 3. `.env` erstellen

Die folgende Vorlage behält die vorgesehene Formatierung und Kommentare bei.

```dotenv
# Domain
DOMAIN=<DOMAIN>

# Docker Images Versions
TRAEFIK_VERSION=3.7
AUTHENTIK_VERSION=2026.5
POSTGRES_VERSION=18

# Authentik Database
POSTGRES_DB=authentik
POSTGRES_USER=authentik

# ACME-Konto
ACME_EMAIL=<ACME_EMAIL>

# ============================================================
# Aktive ACME-Umgebung: Let's Encrypt Staging
# Für Aufbau, Routingtests und Fehlerbehebung verwenden.
# ============================================================
ACME_CA_SERVER=https://acme-staging-v02.api.letsencrypt.org/directory
TRAEFIK_ACME_VOLUME=core_traefik_acme_staging

# ============================================================
# Let's Encrypt Produktion
# Erst aktivieren, wenn alle Tests erfolgreich abgeschlossen sind.
# Dann die beiden Staging-Zeilen oben auskommentieren und
# die beiden folgenden Zeilen aktivieren.
# ============================================================
# ACME_CA_SERVER=https://acme-v02.api.letsencrypt.org/directory
# TRAEFIK_ACME_VOLUME=core_traefik_acme_production
```

Vor dem Speichern müssen `<DOMAIN>` und `<ACME_EMAIL>` durch echte Werte ersetzt werden. Die spitzen Klammern dürfen nicht in der fertigen `.env` stehen.

Datei erstellen:

```bash
nano .env
```

Danach:

```bash
chmod 600 .env
```

### Werte bestimmen

#### `DOMAIN`

Basisdomain ohne Protokoll und ohne Subdomain:

```dotenv
DOMAIN=<DOMAIN>
```

Nicht:

```text
https://<DOMAIN>
auth.<DOMAIN>
```

#### Image-Versionen

Die Werte stammen aus den offiziellen Release-Seiten beziehungsweise Registry-Tags.

Getestete Versionslinien:

```dotenv
TRAEFIK_VERSION=3.7
AUTHENTIK_VERSION=2026.5
POSTGRES_VERSION=18
```

Ein Versionslinien-Tag erhält bei einem bewussten `docker compose pull` Patchupdates derselben Linie.

#### Datenbank

```dotenv
POSTGRES_DB=authentik
POSTGRES_USER=authentik
```

Dies sind keine Secrets. Das Passwort liegt in einer Secret-Datei.

#### `ACME_EMAIL`

Erreichbare E-Mail-Adresse für das ACME-Konto. Sie kann von der Domain abweichen.

#### ACME-Umgebung

Beim ersten Aufbau bleibt Staging aktiv. Der Produktionswechsel wird erst nach vollständiger Prüfung durchgeführt:

- [TLS und Zertifikate](../../tls-und-zertifikate.md)

### `.env` prüfen

```bash
stat -c '%A %n' .env
git check-ignore -v .env
```

Erwartet:

```text
-rw------- .env
```

`git check-ignore` muss mindestens eine Zeile ausgeben, die auf eine `.gitignore`-Regel und die Datei `.env` verweist. Keine Ausgabe bedeutet, dass die Datei nicht ignoriert wird.

Für den Erstaufbau müssen in der Datei diese Werte aktiv sein:

| Variable | Erwarteter Inhalt |
|---|---|
| `DOMAIN` | eigene Basisdomain ohne Protokoll und ohne Subdomain |
| `TRAEFIK_VERSION` | `3.7` |
| `AUTHENTIK_VERSION` | `2026.5` |
| `POSTGRES_VERSION` | `18` |
| `POSTGRES_DB` | `authentik` |
| `POSTGRES_USER` | `authentik` |
| `ACME_EMAIL` | eigene erreichbare E-Mail-Adresse |
| `ACME_CA_SERVER` | `https://acme-staging-v02.api.letsencrypt.org/directory` |
| `TRAEFIK_ACME_VOLUME` | `core_traefik_acme_staging` |

Die beiden Produktionszeilen müssen während des Erstaufbaus auskommentiert bleiben.

Die aufgelösten Compose-Werte werden nach dem Erstellen der Secrets in Schritt 9 geprüft. Die Option `docker compose config --environment` ist nicht in allen Compose-Versionen verfügbar und wird nicht vorausgesetzt.

## 4. Secrets erzeugen

Vorher:

```bash
mkdir -p secrets
umask 077
```

### Authentik Secret Key

```bash
openssl rand -base64 48 \
  | tr -d '\n' \
  > secrets/authentik_secret_key
```

Erklärung:

- `openssl rand` erzeugt kryptografisch sichere Zufallsbytes.
- `48` bedeutet 48 Zufallsbytes.
- Base64 macht die Bytes texttauglich.
- `tr -d '\n'` entfernt den abschließenden Zeilenumbruch.
- Base64 ist keine Verschlüsselung; die Sicherheit entsteht durch den Zufall und die geschützte Datei.

### PostgreSQL-Passwort

```bash
openssl rand -base64 32 \
  | tr -d '\n' \
  > secrets/postgresql_password
```

Das Passwort wird nicht in `.env` gespeichert.

### Rechte

```bash
chmod 600 \
  secrets/authentik_secret_key \
  secrets/postgresql_password
```

Prüfen, ohne Inhalte auszugeben:

```bash
stat -c '%A %s Bytes %n' secrets/*
```

Erwartet bei den hier verwendeten Generierungsbefehlen:

```text
-rw------- 64 Bytes secrets/authentik_secret_key
-rw------- 44 Bytes secrets/postgresql_password
```

Die Reihenfolge der beiden Zeilen kann abweichen. Andere Dateigrößen sind nur dann korrekt, wenn bewusst ein anderes Generierungsverfahren verwendet wurde.

### Secrets nicht nachträglich blind ersetzen

- Ein neues PostgreSQL-Passwort ändert nicht automatisch das Passwort in der bestehenden Datenbank.
- Ein neuer Authentik Secret Key kann verschlüsselte Daten, Sitzungen und bestehende Konfiguration unbrauchbar machen.
- Rotation erfordert ein eigenes Migrationsverfahren.

## 5. Git-Schutz prüfen

```bash
cd <PROJEKT_ROOT>

git check-ignore -v \
  Compose/core/.env \
  Compose/core/secrets/authentik_secret_key \
  Compose/core/secrets/postgresql_password
```

Alle drei Pfade müssen in der Ausgabe erscheinen und durch eine `.gitignore`-Regel ignoriert werden. Keine Ausgabe für einen Pfad bedeutet, dass dieser nicht geschützt ist.

## 6. Netzwerk `web`

```bash
docker network inspect web >/dev/null 2>&1 \
  || docker network create web
```

Prüfen:

```bash
docker network inspect web \
  --format 'Name={{.Name}} Driver={{.Driver}} Scope={{.Scope}}'
```

Erwartet:

```text
Name=web Driver=bridge Scope=local
```

`core_auth` wird erst beim Start von Compose erstellt.

## 7. DNS prüfen

Die Platzhalter vor der Ausführung durch die konfigurierte Domain ersetzen:

```bash
getent ahostsv4 auth.<DOMAIN>
getent ahostsv4 proxy.<DOMAIN>
```

Erwartet: Beide Namen liefern die öffentliche IPv4-Adresse des Servers. Mehrere Zeilen pro Name sind normal.

IPv6 nur bei vorhandenem AAAA-Eintrag:

```bash
getent ahostsv6 auth.<DOMAIN>
getent ahostsv6 proxy.<DOMAIN>
```

Erwartet bei konfiguriertem IPv6: Beide Namen liefern die öffentliche IPv6-Adresse des Servers. Ist bewusst kein AAAA-Eintrag vorhanden, darf die IPv6-Abfrage ohne Ausgabe bleiben.

## 8. Ports prüfen

```bash
sudo ss -lntp | grep -E ':(80|443)\s' || true
```

Erwartet vor dem ersten Start: keine Ausgabe. Jede Ausgabe bedeutet, dass mindestens Port 80 oder 443 bereits belegt ist und der betreffende Prozess zuerst geprüft werden muss.

## 9. Compose-Konfiguration prüfen

```bash
cd <PROJEKT_ROOT>/Compose/core

docker compose config --quiet
docker compose config --services
```

Erwartet für `docker compose config --quiet`: keine Ausgabe und Exit-Code `0`.

Erwartete Dienste; die Reihenfolge kann abweichen:

```text
traefik
postgresql
authentik-server
authentik-worker
```

Aufgelösten ACME-Server prüfen:

```bash
docker compose config \
  | grep -E 'acme\.(storage|caserver)'
```

Volume prüfen:

```bash
docker compose config \
  | grep -A3 'traefik_acme:'
```

Staging erwartet:

```text
--certificatesresolvers.letsencrypt.acme.storage=/acme/acme.json
--certificatesresolvers.letsencrypt.acme.caserver=https://acme-staging-v02.api.letsencrypt.org/directory
name: core_traefik_acme_staging
```

Zusätzlich müssen in `docker compose config` erscheinen:

```text
image: traefik:3.7
image: ghcr.io/goauthentik/server:2026.5
image: postgres:18
target: /run/secrets/postgresql_password
target: /run/secrets/authentik_secret_key
```

Die Authentik-Imagezeile erscheint für Server und Worker jeweils einmal. In Routerregeln müssen `auth.<DOMAIN>` und `proxy.<DOMAIN>` bereits mit der tatsächlich gewählten Domain aufgelöst sein; ein wörtliches `<DOMAIN>` darf dort nicht verbleiben.

## 10. Vorbereitungscheckliste

- [ ] `.env` vollständig ausgefüllt
- [ ] persönliche Domain und E-Mail ersetzt
- [ ] Staging aktiv
- [ ] Secret-Dateien erzeugt
- [ ] Secret-Dateien Modus `600`
- [ ] `.env` Modus `600`
- [ ] Git ignoriert `.env` und `secrets/`
- [ ] Netzwerk `web` existiert
- [ ] DNS stimmt
- [ ] Port 80 und 443 frei
- [ ] `docker compose config --quiet` erfolgreich
