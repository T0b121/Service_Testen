# SearXNG-Stack: Erststart und Prüfung

Vorher müssen [Vorbereiten](vorbereiten.md) und
[Authentik einrichten](authentik-einrichten.md) abgeschlossen sein.

## 1. Starten

```bash
cd <PROJEKT_ROOT>/Compose/searxng
docker compose pull
docker compose up -d
docker compose ps
docker compose logs --tail=100 searxng
```

`searxng` und `searxng-valkey` müssen `Up` sein. Der Stack hat bewusst keinen
HTTP-Healthcheck im Container, weil das offizielle Image kein fest zugesagtes
HTTP-Client-Werkzeug enthält.

Beim ersten Start können einzelne Suchmaschinen eine 403-, 429- oder
CAPTCHA-Meldung protokollieren. Das betrifft nur die jeweilige Engine; SearXNG
nimmt sie zeitweise aus der Suche. Eine Meldung über eine fehlende
`/etc/searxng/limiter.toml` ist dagegen ein Konfigurationsfehler und darf mit
diesem Stack nicht auftreten.

## 2. Öffentlichen Zugriff prüfen

```bash
curl -I https://searxng.<DOMAIN>/outpost.goauthentik.io/ping
curl -I https://searxng.<DOMAIN>/
```

Erwartet:

- der Outpost-Ping liefert `204`,
- der Aufruf von `/` liefert ohne Authentik-Sitzung `302` zur Authentik-Anmeldung.

Danach in einem privaten Browserfenster `https://searxng.<DOMAIN>/` öffnen,
mit einem Mitglied von `searxng-users` anmelden und eine Suche ausführen.

## 3. Interne JSON-API prüfen

Die JSON-API ist für interne Clients gedacht und deshalb nur über das
Docker-Netzwerk erreichbar:

```bash
docker compose exec searxng python -c \
  "from urllib.request import urlopen; print(urlopen('http://localhost:8080/healthz').status)"
```

Erwartet ist `200`.

Die konkrete Prüfung aus einem Client-Container gehört in dessen
Dokumentation. Für Open WebUI steht sie unter
[Websuche mit SearXNG](../open-webui/websuche-mit-searxng.md).

Weiter mit [Betrieb](betrieb.md).
