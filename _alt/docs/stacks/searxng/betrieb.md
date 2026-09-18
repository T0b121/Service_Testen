# SearXNG-Stack: Betrieb

## Interne Suchclients

Interne Anwendungen treten dem Netzwerk `searxng_clients` bei und verwenden
`http://searxng-internal:8080/search`. Das Netz umgeht den SearXNG-Limiter und
darf deshalb nur vertrauenswürdige Suchclients enthalten. Allgemeine Regeln
stehen unter [Dienste](../../dienste.md#hinweise-für-searxng-suchclients).

Die konkrete Open-WebUI-Konfiguration gehört zum Client-Stack und steht unter
[Open WebUI: Websuche mit SearXNG](../open-webui/websuche-mit-searxng.md).

## Regelbetrieb

```bash
cd <PROJEKT_ROOT>/Compose/searxng
docker compose ps
docker compose logs --since=24h
docker compose images
```

SearXNG kann bei einzelnen Suchmaschinen vorübergehende CAPTCHA-, 403- oder
429-Meldungen anzeigen. Das ist meist eine Sperre des jeweiligen Suchanbieters,
nicht ein Fehler des Stacks. Die betroffene Engine wird von SearXNG zeitweise
zurückgestellt.

## Update

1. Release Notes prüfen und die neue SearXNG-Version in der lokalen `.env`
   eintragen.
2. Vor dem Update [Backup](backup-und-wiederherstellung.md) erstellen.
3. Aktualisieren und prüfen:

```bash
docker compose config --quiet
docker compose pull
docker compose up -d
docker compose ps
docker compose logs --tail=100 searxng
```

Bei einem SearXNG-Update die aktuelle offizielle Vorlage für `settings.yml`
auf neue Pflichtoptionen prüfen; die eigene Datei basiert bewusst nur auf
gezielten Abweichungen von den SearXNG-Standardwerten.
