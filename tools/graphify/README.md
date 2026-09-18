# Graphify-Analyse

Die Analyse verwendet Graphify-Labs/graphify 0.9.63 am festgelegten Commit
`26b02b5e3430e4ab85dd7e72c7b98836d8e65c48`. Alle Python-Abhängigkeiten stehen
in `requirements.txt`; sie sind unabhängig von den Laufzeitabhängigkeiten des Managers.

## Neu erstellen

Mit Python 3.12 und Git im Repository:

```sh
python3 -m venv /tmp/service-graphify-venv
/tmp/service-graphify-venv/bin/pip install -r tools/graphify/requirements.txt
/tmp/service-graphify-venv/bin/python tools/graphify/build.py --ref main
```

Das schreibt die HTML-Seiten, den Originalbericht und JSON-Daten nach
`docs/graphify/`. `--ref` akzeptiert einen Commit oder Branch; ohne Angabe wird
`HEAD` verwendet. `--output` erlaubt ein anderes Ausgabeverzeichnis.
Zur lokalen Anzeige: `python3 -m http.server --directory docs/graphify 8080`.

## Umfang

Das Skript exportiert ausschließlich die **committeten** Verzeichnisse `compose/`
und `tests/` in ein temporäres Verzeichnis. Graphify liest den unterstützten Code
lokal mittels AST, gruppiert den Graphen und exportiert die drei Ansichten.
Es werden weder Anwendungshooks ausgeführt noch externe LLM-Dienste angesprochen.
Die HTML-Ansichten verwenden öffentliche CDNs für ihre JavaScript-Bibliotheken.

Markdown und YAML erhalten keine semantische LLM-Analyse. Eine zusätzliche
Stack-Tabelle liest deklarative Werte aus `stack.py` mit `ast.literal_eval`
und die Servicenamen aus `compose.yml` mit `yaml.safe_load`. Der obligatorische
Core wird entsprechend `model.discover` ergänzt. Die Tabelle behauptet keine
vollständige Unterstützung aller Nutzeraktionen durch einen vorhandenen Hook.

`_alt/`, generierte Analysen, lokale Secrets, nicht committete Dateien und
Laufzeitdaten sind ausgeschlossen. Die Kennzeichnung `EXTRACTED` bzw. `INFERRED`
bleibt im Graphen erhalten. Dynamische Beziehungen können fehlen; die Analyse
ersetzt weder Code-Review noch Integrations- oder Sicherheitstests.

## GitHub Pages

Der Workflow `.github/workflows/graphify-pages.yml` baut nach Änderungen an
`main` die Analyse dieses Commits neu und veröffentlicht ausschließlich das
Ausgabeverzeichnis. Für andere Branches wird nicht veröffentlicht. Die im Repo
committeten HTMLs sind eine dokumentierte Momentaufnahme; Pages wird vom Workflow
aktualisiert und kann daher einen neueren Quellstand zeigen.

Einmalig muss in **Settings → Pages → Build and deployment → Source**
**GitHub Actions** ausgewählt sein. Danach kann der Workflow auch manuell über
**Actions → Graphify analysis and Pages → Run workflow** auf `main` gestartet werden.
Keine Branches werden dabei gelöscht. Offene Implementierungs- und Live-Testpunkte
bleiben in Issue #1 dokumentiert.
