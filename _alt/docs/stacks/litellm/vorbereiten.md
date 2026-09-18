# LiteLLM-Stack: Vorbereiten

Vorher müssen der [Core-Stack](../core/erststart-und-pruefung.md) und der
[Ollama-Stack](../ollama/erststart-und-pruefung.md) gesund sein.

## 1. DNS und Netzwerk prüfen

```bash
getent ahostsv4 litellm.<DOMAIN>
getent ahostsv6 litellm.<DOMAIN>
docker network inspect web --format 'Name={{.Name}} Driver={{.Driver}} Scope={{.Scope}}'
```

DNS muss auf den Server zeigen; das Netzwerk muss `web` heißen.

## 2. Lokale Konfiguration anlegen

```bash
cd <PROJEKT_ROOT>/Compose/litellm
nano .env
```

Inhalt:

```dotenv
DOMAIN=<DOMAIN>
LITELLM_VERSION=v1.95.0
POSTGRES_VERSION=18

LITELLM_POSTGRES_DB=litellm
LITELLM_POSTGRES_USER=litellm
# Ausschließlich URL-sichere Zeichen verwenden, z. B. `openssl rand -hex 32`.
LITELLM_POSTGRES_PASSWORD=<ZUFÄLLIGES_HEX_DB_PASSWORT>

# Nur für LiteLLM-Administration; niemals an API-Clients geben.
LITELLM_MASTER_KEY=sk-<ZUFÄLLIGER_MASTER_KEY>
# Muss über die gesamte Lebensdauer der Datenbank unverändert bleiben.
LITELLM_SALT_KEY=<ZUFÄLLIGER_SALT_KEY>

# OIDC-Provider in Authentik: Werte nach dessen Anlage eintragen.
LITELLM_OIDC_CLIENT_ID=<CLIENT_ID>
LITELLM_OIDC_CLIENT_SECRET=<CLIENT_SECRET>

# Lokaler LiteLLM-Fallback hinter Authentik Forward Auth; kein Authentik-Notzugang.
LITELLM_UI_USERNAME=litellm-admin
LITELLM_UI_PASSWORD=<ZUFÄLLIGES_UI_PASSWORT>
```

`LITELLM_POSTGRES_PASSWORD` muss URL-sicher sein, weil Compose daraus die
PostgreSQL-Verbindungs-URL erstellt. Dafür `openssl rand -hex 32` verwenden.
Die übrigen Zufallswerte können beispielsweise mit `openssl rand -base64 48`
erzeugt und direkt in `.env` eingetragen werden. Nie in Git, Logs oder Chats
ausgeben.

```bash
chmod 600 .env
git check-ignore -v .env
```

## 3. Versionierte Konfiguration prüfen

```bash
docker compose config --quiet
```

Die versionierte Datei `config.yaml` stellt zunächst `qwen3:0.6b` aus dem
lokalen Ollama bereit. Weitere Modelle erst nach erfolgreichem Grundtest über
die LiteLLM-Verwaltung ergänzen.

Weiter mit [Authentik einrichten](authentik-einrichten.md).
