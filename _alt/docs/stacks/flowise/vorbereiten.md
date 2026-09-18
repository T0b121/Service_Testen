# Flowise-Stack: Vorbereiten

Vorausgesetzt werden der [Core-Stack](../core/erststart-und-pruefung.md),
[LiteLLM](../litellm/erststart-und-pruefung.md),
[Qdrant](../qdrant/erststart-und-pruefung.md) und
[Neo4j](../neo4j/erststart-und-pruefung.md). Die beiden Client-Netze werden
einmalig angelegt, falls sie nicht bereits mit den jeweiligen Stacks existieren:

```bash
docker network create --internal qdrant_clients
docker network create --internal neo4j_clients
```

Flowise schreibt als Benutzer `1000:1000` in sein Datenvolume. Das externe
Volume wird bewusst vor dem Stack erstellt und einmalig berechtigt:

```bash
docker volume create flowise_data
docker run --rm -v flowise_data:/data alpine:3.24 chown -R 1000:1000 /data
```

`Compose/flowise/.env` ist lokal, wird nicht eingecheckt und muss vor dem Start
vollständig ausgefüllt sein. Die Kommentare bei den Variablen nennen jeweils
eine passende Erzeugungsmethode. Prüfen ohne Werte anzuzeigen:

```bash
cd <PROJEKT_ROOT>/Compose/flowise
chmod 600 .env
docker compose config --quiet
```

| Variablenblock | Zweck |
|---|---|
| `FLOWISE_POSTGRES_*` | dedizierter PostgreSQL-Datenbankzugang |
| `FLOWISE_USERNAME`, `FLOWISE_PASSWORD` | lokaler administrativer Flowise-Zugang; der Benutzername muss eine gültige E-Mail-Adresse sein, z. B. `flowise-admin@<DOMAIN>` |
| `FLOWISE_SECRETKEY_OVERWRITE` | dauerhafter Schlüssel zum Verschlüsseln gespeicherter Flowise-Credentials |
| `FLOWISE_JWT_AUTH_TOKEN_SECRET`, `FLOWISE_JWT_REFRESH_TOKEN_SECRET`, `FLOWISE_EXPRESS_SESSION_SECRET`, `FLOWISE_TOKEN_HASH_SECRET` | voneinander unabhängige Sitzung- und Token-Geheimnisse |

Flowise unterstützt für diese Werte keine Docker-`*_FILE`-Variablen. Sie
bleiben deshalb als `<*...>`-Werte in der lokalen `.env`; sie gehören weder in
Compose-Dateien noch in Git oder Terminalausgaben.

Weiter mit [Authentik einrichten](authentik-einrichten.md).
