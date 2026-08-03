# Open-WebUI-Stack: Fehlerbehebung

## 1. Standarddiagnose

```bash
cd <PROJEKT_ROOT>/Compose/open-webui

docker compose config --quiet
docker compose ps -a
docker compose logs --tail=200 open-webui
docker network inspect web
```

Für die Forward-Auth-Alternative jeden `docker compose`-Befehl durch
`docker compose -f compose.yml -f compose.local-auth.yml` ersetzen.

## 2. Container startet nicht oder ist nicht healthy

```bash
docker inspect open-webui --format '{{json .State.Health}}'
docker compose logs --tail=200 open-webui
stat -c '%A %s Bytes %n' secrets/openwebui_secret_key
```

Der Schlüssel muss vorhanden, nicht leer und `-rw-------` sein.

## 3. OIDC-Anmeldung schlägt fehl

Prüfen:

- DNS für `webui.<DOMAIN>`,
- OAuth2/OpenID Provider `Open WebUI OIDC Provider`,
- Redirect URI `https://webui.<DOMAIN>/oauth/oidc/callback`,
- Client-ID und Client-Secret in `Compose/open-webui/.env`,
- Discovery-URL:

```bash
curl -fsS https://auth.<DOMAIN>/application/o/open-webui/.well-known/openid-configuration
```

Erwartet ist ein JSON-Dokument. Danach die Container-Logs auf `oauth`, `oidc`
oder `redirect` prüfen.

## 4. Authentik meldet `Anfrage wurde verweigert`

Der Benutzer erfüllt keine Gruppenbindung. Mitgliedschaft in
`openwebui-users` oder `openwebui-admin` sowie `Policy engine mode: ANY`
prüfen. Danach neu anmelden.

## 5. Rolle oder Konto stimmt nicht

Den Scope Mapping `Open WebUI Rollen` und seine Zuordnung zum OIDC-Provider
prüfen. Das Mapping muss für `openwebui-users` `user` und für
`openwebui-admin` `admin` zurückgeben. Anschließend vollständig bei Open WebUI
und Authentik abmelden und erneut anmelden.

## 6. Keine Modelle in Open WebUI

```bash
docker compose exec open-webui curl -fsS http://ollama:11434/api/tags

cd <PROJEKT_ROOT>/Compose/ollama
docker compose exec ollama ollama list
```

Beide Container müssen im Netzwerk `web` sein. `OLLAMA_BASE_URL` darf nicht
auf `localhost` oder die externe HTTPS-Adresse zeigen.

## 7. TCP 8080 ist am Host erreichbar

```bash
sudo ss -lntp | grep -E ':(8080)\s' || true
docker compose config
```

Die Compose-Datei darf nur `expose: 8080` enthalten, kein `ports:`-Mapping.

## 8. CORS-Warnung im Startprotokoll

`CORS_ALLOW_ORIGIN` muss auf die öffentliche Adresse begrenzt sein:

```yaml
CORS_ALLOW_ORIGIN: https://webui.<DOMAIN>
```

Nach einer Änderung den Container neu erstellen:

```bash
docker compose up -d --force-recreate open-webui
```
