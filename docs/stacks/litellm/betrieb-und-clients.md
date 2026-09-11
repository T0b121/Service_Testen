# LiteLLM-Stack: Betrieb und Clients

## Verwaltung und Key-Lebenszyklus

Die Oberfläche `https://litellm.<DOMAIN>/ui` verwendet LiteLLM-OIDC gegen
Authentik. Der Master-Key verbleibt beim Administrator. Für jedes Drittsystem
einen separaten Virtual Key anlegen, Modellfreigaben und Limits setzen und den
Zweck dokumentieren. Der lokale Fallback-Login unter `/fallback/login` ist nur
für Störungen des nativen LiteLLM-OIDC-Logins gedacht. Er liegt weiterhin
hinter Authentik Forward Auth und funktioniert daher nicht als Umgehung bei
einem vollständigen Authentik-Ausfall.

Bei Verlust oder Ablösung eines Systems dessen Virtual Key widerrufen statt
einen gemeinsamen Key weiterzuverwenden.

Für produktive Maschinenclients den Key einem `Service Account` zuordnen und
die Modellfreigabe auf die tatsächlich benötigten Modelle beschränken. Der
Test-Key eines persönlichen Administratorkontos ist kein Ersatz dafür.

## Lokale Ollama-Modelle und Agenten

Für normale lokale Textanfragen kann ein Modell in der LiteLLM-Oberfläche mit
dem Provider **Ollama** angelegt werden. Für Chatverläufe, Thinking und
insbesondere n8n-Agenten mit Tools muss dagegen **Ollama Chat** gewählt
werden. Dieser Provider verwendet Ollamas Chat-Schnittstelle und übergibt
native Tool-Calls korrekt.

Für das lokale Modell `qwen3.5:9b` ist die funktionierende Registrierung:

| Feld | Wert |
|---|---|
| Provider | `Ollama Chat` |
| LiteLLM Model Name | `qwen3.5:9b` |
| Public Model Name | frei wählbarer Alias, zum Beispiel `qwen3.5:9b-tools` |
| API Base | `http://ollama:11434` |
| Model Info | `{"mode":"chat","supports_function_calling":true}` |

Der Alias muss anschließend dem jeweiligen Virtual Key explizit freigegeben
werden. Die frühere Registrierung desselben Modells mit Provider **Ollama**
ist für Agenten mit MCP- oder SearXNG-Tools ungeeignet und sollte nach einem
erfolgreichen Test entfernt werden.

## Optionaler Neo4j-MCP-Gateway

Neo4j wird nicht automatisch als LiteLLM-MCP-Server angelegt. Die
`neo4j_clients`-Netzanbindung erlaubt ausschließlich eine bewusst manuell in
der LiteLLM-Oberfläche konfigurierte Integration. Das ist wichtig, weil Neo4j
im späteren Installer optional bleiben soll.

Für eine manuelle Eintragung gilt:

| Feld | Wert |
|---|---|
| Transport | Streamable HTTP |
| MCP Server URL | `http://neo4j-mcp/db/neo4j/mcp` |
| Authentifizierung | `None` |
| Statischer Header `Authorization` | `Basic <BASE64_NEO4J_BENUTZER:PASSWORT>` |
| Statischer Header `X-Neo4j-MCP-URI` | `bolt://neo4j:7687` |
| Statischer Header `X-Neo4j-MCP-ReadOnly` | `false` |
| Zugriff | `Internal network only` aktivieren |

Der Headerwert für `Authorization` enthält das Wort `Basic`, ein Leerzeichen
und den vollständigen Base64-Wert einschließlich einer möglichen `=`- oder
`==`-Auffüllung. Er wird aus dem Neo4j-Secret erzeugt und niemals in
Dokumentation, Git oder Terminal-Historie gespeichert. Der MCP-Server wird
einem Virtual Key gezielt zugeordnet; `Allow All LiteLLM Keys` bleibt aus.

## OpenAI-kompatibler Client

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://litellm.<DOMAIN>/v1",
    api_key="<VIRTUAL_KEY>",
)

response = client.chat.completions.create(
    model="qwen3:0.6b",
    messages=[{"role": "user", "content": "Antworte ausschließlich mit OK."}],
)
print(response.choices[0].message.content)
```

Die API erwartet genau einen Header `Authorization: Bearer <VIRTUAL_KEY>`.
Authentik-Tokens oder der LiteLLM-Master-Key gehören nicht auf Client-Systeme.

## Update und Status

```bash
cd <PROJEKT_ROOT>/Compose/litellm
docker compose ps
docker compose logs --tail=200 litellm
docker compose pull
docker compose up -d
```

Vor jedem Update Release Notes prüfen. `LITELLM_MASTER_KEY` und
`LITELLM_SALT_KEY` niemals während eines Updates ersetzen.
