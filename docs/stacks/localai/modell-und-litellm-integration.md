# Ministral 3 8B: LocalAI- und LiteLLM-Integration

Diese Dokumentation beschreibt die funktionierende Integration des lokal
installierten Modells `mistralai_ministral-3-8b-instruct-2512-multimodal`.
Sie enthält bewusst keine API-Schlüssel, Zugangsdaten oder Domainnamen.

## Architektur

```text
n8n / Flowise / Open WebUI
        |
        | OpenAI-kompatible API, dienstbezogener LiteLLM Virtual Key
        v
LiteLLM  (http://litellm:4000/v1, internes Docker-Netz)
        |
        | OpenAI-kompatible API, LocalAI API-Key
        v
LocalAI  (http://localai:8080/v1, internes Docker-Netz)
        |
        v
Ministral 3 8B Instruct 2512, Q4_K_M GGUF
```

Die Dienste sprechen ausschliesslich über Docker-Netze miteinander. LocalAI
und LiteLLM veröffentlichen dabei keinen zusätzlichen Host-Port.

## LocalAI-Modell

Aktiver LocalAI-Modellname:

```text
mistralai_ministral-3-8b-instruct-2512-multimodal
```

Modell- und Projektionsdateien:

```text
llama-cpp/models/mistralai_Ministral-3-8B-Instruct-2512-Q4_K_M.gguf
llama-cpp/mmproj/mmproj-mistralai_Ministral-3-8B-Instruct-2512-f32.gguf
```

Die für Tool-Calls relevante Modellkonfiguration lautet:

```yaml
backend: llama-cpp
context_size: 16384
mmap: true

function:
  disable_no_action: true
  automatic_tool_parsing_fallback: true
  grammar:
    disable: true
    disable_parallel_new_lines: true
    parallel_calls: true
  return_name_in_function_response: true

template:
  use_tokenizer_template: true
  join_chat_messages_by_character: ""

options:
  - use_jinja:true
```

`parameters.model` und `mmproj` müssen auf die oben genannten Dateien zeigen.
Die getestete Temperatur beträgt `0.15`.

### Warum diese Konfiguration wichtig ist

Ministral 3 besitzt eine eigene Chat- und Tool-Call-Vorlage, die in der GGUF
Datei eingebettet ist. `use_tokenizer_template: true` verwendet genau diese
Vorlage. `automatic_tool_parsing_fallback: true` überführt die nativen
Tool-Call-Tokens in das OpenAI-Format `tool_calls`.

Keine eigene `template.chat`, `template.chat_message` oder
`template.function` definieren. Ebenso keine eigene `json_regex_match`- oder
`replace_function_results`-Logik ergänzen. Die frühere manuelle Vorlage führte
entweder zu nicht erkannten Tool-Aufrufen oder zu wiederholten Tool-Calls ohne
Abschlussantwort.

Die generische LocalAI-Tool-Grammatik bleibt deaktiviert
(`function.grammar.disable: true`). Sie darf für dieses Modell nicht als
Ersatz für die native Tokenizer-Vorlage aktiviert werden, da dies in Tests
Tool-Schleifen verursachte.

Nach einer Änderung der Modellkonfiguration LocalAI bzw. das Modell neu laden,
damit die laufende Backend-Instanz die neue Konfiguration verwendet.

## LiteLLM-Einbindung

In LiteLLM wird das Modell über **Models + Endpoints → Add Model** als
OpenAI-kompatibler Upstream hinterlegt.

Gemeinsame Upstream-Werte:

```text
Upstream API Base: http://localai:8080/v1
Upstream Model ID: mistralai_ministral-3-8b-instruct-2512-multimodal
API Key: ein in LocalAI angelegter dienstbezogener Schlüssel
```

Für die Vergleichstests existieren zwei öffentliche LiteLLM-Modellnamen:

```text
ministral-3-8b_OpenAI
ministral-3-8b_OpenAI-Compatible Endpoints
```

Beide referenzieren dasselbe LocalAI-Modell. Sie sind daher keine zwei
unabhängigen Modelle und ihre Requests teilen sich denselben LocalAI-Backend-
Prozess. Für einen normalen Client sollte ein klar benannter Modellalias
verwendet werden; die zwei obigen Namen dienen primär dem Providervergleich.

Jeder aufrufende Dienst erhält einen eigenen LiteLLM Virtual Key. Dieser Key
wird nur beim jeweiligen Client hinterlegt; der LocalAI-Upstream-Key bleibt
innerhalb von LiteLLM.

## n8n-Referenz

Für den OpenAI Chat Model-Node in n8n:

```text
Base URL: http://litellm:4000/v1
API Key: eigener n8n LiteLLM Virtual Key
Model: einer der in LiteLLM angelegten Modellaliases
Responses API: deaktiviert
```

Die Tool-Verbindung erfolgt am AI-Agenten, zum Beispiel SearXNG für Recherche
oder Calculator für Berechnungen. Ein erfolgreicher Test zeigt einen
`tool_calls`-Schritt in `intermediateSteps`, führt das Tool aus und gibt danach
eine normale Abschlussantwort zurück.

Bei verpflichtenden Aktionen, etwa „immer zuerst suchen“, ist ein n8n-
Workflow-Schritt mit direktem Tool-Aufruf belastbarer als die Entscheidung
durch ein Sprachmodell. Ein AI-Agent kann Tool-Nutzung gut veranlassen, aber
nicht mathematisch garantiert erzwingen.

## Prüfung nach Änderungen

1. LocalAI-Modell neu laden.
2. In LiteLLM die Verbindung zum Modell testen.
3. In n8n zunächst einen einzelnen Calculator-Agenten ausführen. Erwartung:
   genau ein Calculator-Aufruf und danach das Rechenergebnis.
4. Danach einen einzelnen Recherche-Agenten mit SearXNG testen. Erwartung:
   mindestens ein SearXNG-Aufruf und danach eine Textantwort.
5. Erst zuletzt mehrere Agenten parallel testen. Alle Vergleichsagenten teilen
   sich das eine LocalAI-Modell; längere Laufzeiten sind daher erwartbar.
