# SearXNG-Stack: Fehlerbehebung

## Öffentliche Seite liefert sofort SearXNG statt einer Authentik-Anmeldung

Prüfen, ob die Anwendung `SearXNG Access` dem **authentik Embedded Outpost**
zugeordnet ist. Der Traefik-Router `searxng` muss das Middleware-Label
`authentik@docker` besitzen; danach den Stack neu erstellen:

```bash
cd <PROJEKT_ROOT>/Compose/searxng
docker compose up -d --force-recreate searxng
```

## Authentik zeigt nach dem Login „Not Found"

Im Proxy Provider muss der `External host` exakt
`https://searxng.<DOMAIN>` lauten – ohne Pfad und ohne abschließenden Slash.
Danach die Outpost-Zuordnung prüfen und den Browser-Login erneut starten.

## SearXNG startet nicht oder der Limiter meldet Valkey-Fehler

```bash
cd <PROJEKT_ROOT>/Compose/searxng
docker compose ps
docker compose logs --tail=150 searxng searxng-valkey
docker compose exec searxng python -c \
  "from urllib.request import urlopen; print(urlopen('http://localhost:8080/healthz').status)"
```

`SEARXNG_VALKEY_URL` wird im Compose-Stack auf
`valkey://searxng-valkey:6379/0` gesetzt. Der Valkey-Dienst darf deshalb nicht
aus dem internen Netzwerk entfernt oder umbenannt werden.

## `missing config file: /etc/searxng/limiter.toml`

Die versionierte Datei `Compose/searxng/config/limiter.toml` muss vorhanden
und im Container eingehängt sein. Danach neu erstellen:

```bash
cd <PROJEKT_ROOT>/Compose/searxng
docker compose up -d --force-recreate searxng
```

## Open WebUI erhält keine Websuchergebnisse

Netzwerk-, Modell- und Chatdiagnose stehen beim Client unter
[Open WebUI: Websuche mit SearXNG](../open-webui/websuche-mit-searxng.md#6-fehlerbehebung).
