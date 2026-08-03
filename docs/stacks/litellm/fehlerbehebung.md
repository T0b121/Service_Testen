# LiteLLM-Stack: Fehlerbehebung

## Standarddiagnose

```bash
cd <PROJEKT_ROOT>/Compose/litellm
docker compose config --quiet
docker compose ps -a
docker compose logs --tail=200 litellm litellm-postgresql
docker network inspect web
```

## API liefert `401` oder `403`

Prüfen:

- der Client nutzt `https://litellm.<DOMAIN>/v1`,
- der Header lautet `Authorization: Bearer <VIRTUAL_KEY>`,
- der Virtual Key ist aktiv und für `qwen3:0.6b` freigegeben,
- es wird nicht der LiteLLM-Master-Key oder ein Authentik-Token verwendet.

## LiteLLM startet wiederholt neu und meldet einen Datenbankfehler

`LITELLM_POSTGRES_PASSWORD` ist Teil der PostgreSQL-Verbindungs-URL. Es darf
deshalb keine URL-reservierten Zeichen enthalten. Einen neuen Wert mit
`openssl rand -hex 32` erzeugen. Bei einer frischen, noch unbenutzten
Installation muss anschließend auch das LiteLLM-PostgreSQL-Volume neu erzeugt
werden, damit dessen Datenbankpasswort zum neuen `.env`-Wert passt.

## `/ui` zeigt keinen SSO-Login oder die Rückleitung schlägt fehl

Prüfen:

- OIDC-Provider `LiteLLM OIDC Provider`,
- Gruppenbindung `litellm-admin`,
- `LITELLM_OIDC_CLIENT_ID` und `LITELLM_OIDC_CLIENT_SECRET` in `.env`,
- `PROXY_BASE_URL=https://litellm.<DOMAIN>`,
- Redirect URI in Authentik:

```bash
https://litellm.<DOMAIN>/sso/callback
```

Die Endpunkte in der Compose-Umgebung müssen für Authentik ohne den
Anwendungs-Slug lauten: `/application/o/authorize/`,
`/application/o/token/` und `/application/o/userinfo/`. Die verbindliche
Quelle ist die Discovery-URL
`https://auth.<DOMAIN>/application/o/litellm/.well-known/openid-configuration`.

## Modell nicht verfügbar

```bash
docker compose exec litellm curl -fsS http://ollama:11434/api/tags
docker compose exec litellm \
  curl -fsS http://localhost:4000/v1/models \
  -H 'Authorization: Bearer <LITELLM_MASTER_KEY>'
```

Ollama muss `qwen3:0.6b` liefern. Danach `config.yaml` auf den gleichen
Modellnamen prüfen und LiteLLM neu erstellen:

```bash
docker compose up -d --force-recreate litellm
```
