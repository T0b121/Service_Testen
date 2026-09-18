# Nextcloud-Stack: Vorbereiten

Vorher abschließen:

- [Core: Erststart und Prüfung](../core/erststart-und-pruefung.md)
- [Jellyfin: Erststart und Prüfung](../jellyfin/erststart-und-pruefung.md)

## Lokale `.env` anlegen

```bash
cd <PROJEKT_ROOT>/Compose/nextcloud
nano .env
```

Vollständiger Inhalt:

```dotenv
# Basisdomain; die öffentlichen Adressen sind cloud.${DOMAIN} und office.${DOMAIN}.
DOMAIN=<DOMAIN>

# Nextcloud-34-Patch-Linie mit Apache-Webserver. Traefik spricht HTTP, aber
# kein FastCGI. "34-apache" erhält 34.x-Sicherheitsupdates, aber kein 35er-Upgrade.
NEXTCLOUD_VERSION=34-apache

# Aktuelle PostgreSQL-18-Patch-Linie für eine neue Nextcloud-Installation.
POSTGRES_VERSION=18

# Aktuelle Redis-8-Patch-Linie auf kleiner Alpine-Basis.
REDIS_VERSION=8-alpine

# Nur für den einmaligen Berechtigungs-Hilfscontainer des Jellyfin-Medienvolumes.
ALPINE_VERSION=3.24

# Aktuell geprüfte ONLYOFFICE-Version. Kein "latest": der Hersteller führt
# keinen zuverlässig mit 9.4.x fortgeschriebenen Linien-Tag. Neue Sicherheits-
# und Bugfix-Releases werden deshalb nach Prüfung bewusst hier eingetragen.
ONLYOFFICE_VERSION=9.4.0.1

# Nicht geheime Nextcloud-Datenbankkennungen.
POSTGRES_DB=nextcloud
POSTGRES_USER=nextcloud

# Name des beim ersten Start erzeugten lokalen Nextcloud-Administrators.
NEXTCLOUD_ADMIN_USER=admin

# PHP-Limits für die Nextcloud-Weboberfläche.
PHP_MEMORY_LIMIT=1024M
PHP_UPLOAD_LIMIT=10G
```

Anschließend `.env` mit Modus `600` schützen und per `git check-ignore -v .env`
prüfen. Die Datei enthält keine Passwörter und wird nicht eingecheckt.

## Secrets erzeugen

```bash
cd <PROJEKT_ROOT>/Compose/nextcloud
umask 077
mkdir -p secrets
chmod 700 secrets
openssl rand -base64 36 | tr -d '\n' > secrets/postgresql_password
openssl rand -base64 36 | tr -d '\n' > secrets/nextcloud_admin_password
openssl rand -base64 48 | tr -d '\n' > secrets/onlyoffice_jwt_secret
chmod 600 .env secrets/*
```

Die Werte dauerhaft im Passwortmanager sichern. Das JWT-Secret muss für
ONLYOFFICE und die Nextcloud-ONLYOFFICE-App identisch bleiben.

## DNS, Netzwerk und Medienvolume prüfen

```bash
getent ahostsv4 cloud.<DOMAIN>
getent ahostsv6 cloud.<DOMAIN>
getent ahostsv4 office.<DOMAIN>
getent ahostsv6 office.<DOMAIN>
docker network inspect web --format 'Name={{.Name}} Driver={{.Driver}} Scope={{.Scope}}'
docker volume inspect jellyfin_media
```

Beide Namen müssen auf den Server zeigen. `web` und `jellyfin_media` müssen
bereits existieren. ONLYOFFICE benötigt beim ersten Pull ungefähr 1,3 GB
Image-Speicher und deutlich mehr RAM als Nextcloud allein.

Zum Abschluss im Stack-Verzeichnis `docker compose config --quiet` ausführen.
Erwartet: keine Ausgabe und Exit-Code `0`.

Weiter mit [Authentik einrichten](authentik-einrichten.md).
