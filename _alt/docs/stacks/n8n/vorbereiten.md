# n8n-Stack: Vorbereiten

Vorausgesetzt werden der [Core-Stack](../core/erststart-und-pruefung.md),
[LiteLLM](../litellm/erststart-und-pruefung.md) und
[SearXNG](../searxng/erststart-und-pruefung.md). Qdrant und Neo4j sind nur
erforderlich, falls n8n sie verwenden soll.

`Compose/n8n/.env` ist die lokale Betriebsdatei, wird nicht eingecheckt und
muss vor dem Start vollständig ausgefüllt sein. Kommentare in der Datei
erklären jeden Wert. Sie enthält insbesondere:

| Variablenblock | Zweck |
|---|---|
| `DOMAIN`, `N8N_VERSION`, `POSTGRES_VERSION` | feste Stack- und Adressparameter |
| `N8N_POSTGRES_*` | dedizierter PostgreSQL-Zugang |
| `N8N_ENCRYPTION_KEY` | verschlüsselt gespeicherte n8n-Credentials; dauerhaft sichern |
| `N8N_RUNNERS_AUTH_TOKEN` | eigener Token zwischen n8n und externen Runners |

Alle geheimen Werte sind voneinander unabhängig. n8n bietet für diese
Variablen keine durchgängig nutzbaren Docker-`*_FILE`-Schnittstellen; sie
bleiben als reguläre lokale Umgebungsvariablen in der geschützten `.env`.

```bash
cd <PROJEKT_ROOT>/Compose/n8n
chmod 600 .env
docker compose config --quiet
```

Die Netzwerke `qdrant_clients`, `neo4j_clients` und `searxng_clients` müssen
nur existieren, wenn sie im Compose-Stack referenziert werden. Sie werden von
den jeweiligen Stacks angelegt.

Weiter mit [Authentik einrichten](authentik-einrichten.md).
