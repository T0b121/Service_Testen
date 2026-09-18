# Langfuse-Stack: Vorbereiten

Vorausgesetzt werden der [Core-Stack](../core/erststart-und-pruefung.md) und
der [RustFS-Stack](../rustfs/erststart-und-pruefung.md). Das interne Netzwerk
für LiteLLM wird einmalig angelegt:

```bash
docker network create --internal langfuse_clients
```

`Compose/langfuse/.env` ist lokal, wird nicht eingecheckt und enthält die
Versions-, Datenbank- und Zugangswerte. Alle Zeilen müssen gefüllt sein.

| Variablenblock | Zweck |
|---|---|
| `LANGFUSE_POSTGRES_*`, `LANGFUSE_CLICKHOUSE_*`, `LANGFUSE_VALKEY_PASSWORD` | voneinander unabhängige Backend-Zugänge |
| `LANGFUSE_SALT`, `LANGFUSE_NEXTAUTH_SECRET`, `LANGFUSE_INIT_USER_PASSWORD` | normale, imagekompatible Passwortwerte |
| `LANGFUSE_ENCRYPTION_KEY` | exakt 64 Hex-Zeichen, erzeugbar mit `openssl rand -hex 32` |
| `LANGFUSE_OIDC_CLIENT_SECRET` | OAuth2-Client-Secret für Authentik |
| `LANGFUSE_PROJECT_PUBLIC_KEY`, `LANGFUSE_PROJECT_SECRET_KEY` | eigenes LiteLLM-Projekt-Zugangspaar |
| `RUSTFS_LANGFUSE_ACCESS_KEY`, `RUSTFS_LANGFUSE_SECRET_KEY` | eigener RustFS-Service-Account für den Bucket `langfuse` |

Langfuse v4 akzeptiert für diese Werte keine `*_FILE`-Variablen. Sie liegen
daher als `<*...>`-Fallback in der lokalen `.env`, niemals in Compose, Git oder
Terminal-Ausgaben. Jeder Wert ist eigenständig; insbesondere dürfen Datenbank-,
OIDC-, Initialpasswort- und S3-Zugang nicht wiederverwendet werden.

Die Werte `LANGFUSE_ADMIN_EMAIL` und `LANGFUSE_ADMIN_NAME` dienen nur dem
headless Erststart. Die E-Mail muss der E-Mail des entsprechenden
Authentik-Profils entsprechen, damit Authentik-OIDC denselben Langfuse-Account
verknüpft. Die normale Anmeldung erfolgt danach ausschließlich über SSO.

Prüfung ohne Offenlegung von Werten:

```bash
cd <PROJEKT_ROOT>/Compose/langfuse
chmod 600 .env
docker compose config --quiet
```

Weiter mit [Authentik einrichten](authentik-einrichten.md).
