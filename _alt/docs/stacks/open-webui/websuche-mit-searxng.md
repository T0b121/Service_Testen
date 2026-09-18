# Open WebUI: Websuche mit SearXNG

Diese Anleitung beschreibt die vollständige, getestete Anbindung von SearXNG
als `search_web`-Werkzeug in Open WebUI. Eine erreichbare SearXNG-Webseite
allein genügt nicht: Netzwerk, globale Suchkonfiguration, Modellfreigaben und
Chatfunktion müssen zusammenpassen.

## 1. Voraussetzungen und internes Netzwerk

Vorher müssen [SearXNG](../searxng/erststart-und-pruefung.md) und
[Open WebUI](erststart-und-pruefung.md) laufen.

```bash
docker network inspect searxng_clients \
  --format '{{range .Containers}}{{.Name}} {{end}}'
```

Die Ausgabe muss `searxng` und `open-webui` enthalten. Open WebUI verwendet
bewusst den nur in diesem Netz vorhandenen Alias `searxng-internal`. Der Name
`searxng` würde wegen des zusätzlich gemeinsamen Netzwerks `web` möglicherweise
auf die falsche Containeradresse zeigen und vom SearXNG-Limiter abgewiesen.

Verbindung und JSON-Ausgabe direkt aus Open WebUI prüfen:

```bash
cd <PROJEKT_ROOT>/Compose/open-webui
docker compose exec open-webui \
  curl -fsS 'http://searxng-internal:8080/search?q=Open+WebUI&format=json' \
  | jq -e '.results | length > 0'
```

Erwartet ist `true`.

## 2. Globale Websuche konfigurieren

In Open WebUI als Administrator zu
**Einstellungen → Administrator → Werkzeuge → Websuche** wechseln und setzen:

```text
Websuche: An
Websuche-Bestätigung: Aus
Web-Suchmaschine: searxng
Searxng-Abfrage-URL: http://searxng-internal:8080/search?q=<query>
SearXNG-Suchsprache: all
Anzahl der Suchergebnisse: 3
Gleichzeitige Anfragen: 1
Embedding und Retrieval umgehen: Aus
Web-Loader umgehen: Aus
```

`Proxy-Umgebung vertrauen` darf aktiviert bleiben. Ohne konfigurierte
`HTTP_PROXY`-/`HTTPS_PROXY`-Variablen ändert der Schalter den direkten internen
SearXNG-Aufruf nicht. Danach **Speichern** wählen.

Der Platzhalter `<query>` muss unverändert in der URL stehen. Open WebUI
ergänzt für die Abfrage selbst das JSON-Format; SearXNG erlaubt `json` bereits
in seiner versionierten `settings.yml`.

## 3. Modell für die Websuche konfigurieren

Unter **Einstellungen → Administrator → AI → Modelle** das gewünschte Modell
öffnen. Für ein kleines lokales Modell wie `gemma4:e4b` hat sich folgende
reduzierte Konfiguration als zuverlässig erwiesen:

```text
Erweiterte Parameter → Funktionsaufruf: Nativ

Fähigkeiten:
  Websuche: An
  Eingebaute Werkzeuge: An

Standardfunktionen:
  Websuche: An

Eingebaute Werkzeuge:
  Websuche: An
  alle anderen Werkzeuge: Aus
```

Anschließend **Speichern & Aktualisieren** wählen. Bei kleinen Modellen können
viele gleichzeitig übergebene Werkzeugschemas dazu führen, dass das später
angehängte `search_web` nicht mehr zuverlässig erkannt wird. Falls Aufgaben,
Kalender oder andere Werkzeuge benötigt werden, deshalb besser ein separates
Modellprofil für die Websuche anlegen.

Größere, zuverlässig tool-fähige Modelle können weitere Werkzeuge erhalten.
Für jeden Modelltyp muss aber mindestens die Capability `Websuche`, der
Hauptschalter `Eingebaute Werkzeuge` und das eingebaute Werkzeug `Websuche`
aktiv sein.

## 4. Websuche im Chat testen

Nach einer Modelländerung einen **neuen Chat** öffnen. Das Globus-Symbol muss
blau beziehungsweise die Websuche muss aktiviert sein.

Eindeutiger Funktionstest:

```text
Verwende zuerst zwingend das Werkzeug search_web und suche nach
"site:docs.searxng.org SearXNG Installation container".

Nenne anschließend die Titel und vollständigen URLs der ersten drei
Suchergebnisse. Verwende kein eigenes Modellwissen. Falls search_web nicht
verfügbar ist, antworte exakt mit TOOL_FEHLT.
```

Erwartet wird:

- ein sichtbarer Aufruf `search_web`,
- die Eingabe der Suchanfrage,
- eine Ergebnisliste mit `title`, `link` und `snippet`,
- eine abschließende Antwort mit den gefundenen Quellen.

Eine reine Textantwort ohne sichtbaren Werkzeugaufruf beweist keine
funktionierende Websuche.

## 5. Nachrichten- und Recherchetest

Für eine orts- und zeitbezogene Recherche die Suchschritte ausdrücklich
vorgeben:

```text
Verwende search_web mit diesen beiden Suchanfragen:

1. "Rathenow aktuelle Nachrichten <HEUTIGES_DATUM>"
2. "Rathenow aktuelle Meldungen"

Berücksichtige ausschließlich Ergebnisse, die sich eindeutig auf Rathenow
beziehen. Nutze nur die von search_web gelieferten Quellen. Fasse die drei
relevantesten Meldungen anschließend in Stichpunkten zusammen und nenne zu
jeder Meldung Quelle, URL und Veröffentlichungsdatum. Falls kein Datum
erkennbar ist, schreibe "Datum nicht erkennbar".
```

`<HEUTIGES_DATUM>` vor dem Test durch das aktuelle ausgeschriebene Datum
ersetzen.

## 6. Fehlerbehebung

### Direkter Test liefert `429`

Prüfen, dass die URL `searxng-internal` und nicht `searxng` verwendet. Danach:

```bash
docker compose exec open-webui getent ahostsv4 searxng-internal
```

Die Adresse muss aus `172.20.0.0/24` stammen. Das Subnetz ist in der
SearXNG-Limiter-Konfiguration ausschließlich für vertrauenswürdige interne
Suchclients freigestellt.

### Modell meldet `TOOL_FEHLT`

1. `Funktionsaufruf` auf `Nativ` setzen.
2. Capability, Standardfunktion und eingebautes Werkzeug `Websuche` prüfen.
3. Alle anderen eingebauten Werkzeuge testweise deaktivieren.
4. Speichern, Oberfläche neu laden und einen neuen Chat beginnen.
5. Das blaue Globus-Symbol kontrollieren.

### Suche läuft, aber einzelne Quellen fehlen

```bash
cd <PROJEKT_ROOT>/Compose/searxng
docker compose logs --tail=150 searxng
```

CAPTCHA-, 403- und 429-Meldungen einzelner Suchanbieter sind keine Störung der
Open-WebUI-Anbindung. SearXNG setzt die jeweilige Engine vorübergehend aus und
verwendet weiterhin verfügbare Quellen.

Weitere SearXNG-spezifische Fehler stehen unter
[SearXNG: Fehlerbehebung](../searxng/fehlerbehebung.md).
