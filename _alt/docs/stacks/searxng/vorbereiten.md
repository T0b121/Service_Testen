# SearXNG-Stack: Vorbereiten

Vorher muss der [Core-Stack](../core/erststart-und-pruefung.md) gesund sein.

## 1. DNS und Netzwerk prüfen

```bash
getent ahostsv4 searxng.<DOMAIN>
getent ahostsv6 searxng.<DOMAIN>
docker network inspect web --format 'Name={{.Name}} Driver={{.Driver}} Scope={{.Scope}}'
```

DNS muss auf den Server zeigen; das externe Docker-Netzwerk muss `web` heißen.
Das für Suchclients reservierte Subnetz `172.20.0.0/24` darf sich nicht mit
einem vorhandenen Docker- oder Standortnetz überschneiden. Hinweise für eine
bewusste Änderung stehen unter
[Dienste](../../dienste.md#hinweise-für-searxng-suchclients).

## 2. Lokale Konfiguration anlegen

```bash
cd <PROJEKT_ROOT>/Compose/searxng
nano .env
```

Inhalt:

```dotenv
# Basisdomain: Die öffentliche Oberfläche lautet searxng.${DOMAIN}.
DOMAIN=<DOMAIN>

# Fest gepinnte SearXNG-Version; niemals "latest" verwenden.
SEARXNG_VERSION=2026.8.4-c63835bd2

# Valkey versorgt den SearXNG-Rate-Limiter und bleibt nur intern erreichbar.
VALKEY_VERSION=9-alpine

# Einmal mit "openssl rand -base64 48" erzeugen und dauerhaft unverändert
# lassen. Der Wert ist geheim und darf weder in Git noch in Logs erscheinen.
SEARXNG_SECRET=<ZUFÄLLIGER_SECRET>
```

Den Secret-Wert erzeugen und unmittelbar in `.env` eintragen:

```bash
openssl rand -base64 48
chmod 600 .env
git check-ignore -v .env
```

`SEARXNG_SECRET` darf nach dem ersten Start nicht geändert werden, da er unter
anderem für signierte Einstellungen und Cookies verwendet wird. Er gehört nie
in Git, Logs oder Chats.

Die aktuell geprüfte SearXNG-Version ist bewusst fest gepinnt. Das verhindert,
dass `docker compose pull` unbeabsichtigt `latest` übernimmt.

## 3. Versionierte Konfiguration prüfen

```bash
docker compose config --quiet
```

Weiter mit [Authentik einrichten](authentik-einrichten.md).
