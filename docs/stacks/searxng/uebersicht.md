# SearXNG-Stack: Übersicht

SearXNG bündelt Suchmaschinen ohne eigenes Benutzertracking. Der Stack besteht
aus SearXNG und Valkey für den eingebauten Rate-Limiter.

| Komponente | Aufgabe |
|---|---|
| SearXNG | Suchoberfläche und JSON-Such-API |
| Valkey | Rate-Limiter und Bot-Schutz |

Die Browseroberfläche unter `https://searxng.<DOMAIN>` wird vor der
Auslieferung durch Authentik Forward Auth geschützt. Der JSON-Endpunkt ist
nicht öffentlich freigegeben: Anwendungen im Docker-Netzwerk erreichen ihn
direkt unter `http://searxng-internal:8080/search`.

SearXNG ist am externen Netzwerk `web` für Traefik, am ausschließlich
internen Netzwerk `searxng_internal` für Valkey und am internen,
festen Client-Netz `searxng_clients` für Open WebUI angeschlossen. Nur
`searxng_clients` umgeht die SearXNG-Bot-Erkennung für die interne JSON-Suche;
die öffentliche Oberfläche bleibt weiterhin geschützt und rate-limitiert. Die
Volumes `searxng_cache` und `searxng_valkey_data` halten Cache beziehungsweise
Limiter-Daten fest.

Voraussetzung ist ein gesunder [Core-Stack](../core/erststart-und-pruefung.md).
Für die spätere Nutzung als Websuche ist [Open WebUI](../open-webui/uebersicht.md)
optional.

Weiter mit [Vorbereiten](vorbereiten.md).
