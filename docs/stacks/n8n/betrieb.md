# n8n-Stack: Betrieb

## LiteLLM-Credential

Für n8n wird ein eigener LiteLLM-Virtual-Key verwendet. Im n8n-Credential des
Nodes **OpenAI Chat Model** lautet die Base URL `http://litellm:4000/v1`; der
API-Key ist der vollständige `sk-...`-Virtual-Key. Der Schlüssel wird weder
als Key-ID noch als Authentik-Token eingetragen.

Für den **MCP Client** wird ein separates n8n-Header-Credential angelegt:

```text
Header name: Authorization
Value: Bearer <LITELLM_N8N_VIRTUAL_KEY>
```

Dasselbe LiteLLM-Secret darf in diesen zwei n8n-Credentials verwendet werden;
es handelt sich um denselben Maschinenclient. Der Virtual Key muss jedoch
nur die benötigten Modelle und die ausdrücklich freigegebenen MCP-Server
erhalten.

## Privater Neo4j-Memory-Chat

Der getestete Workflow besteht aus:

```text
When chat message received → AI Agent → Code in JavaScript
                              ├── OpenAI Chat Model (LiteLLM)
                              ├── MCP Client (LiteLLM → Neo4j)
                              └── SearXNG (optional)
```

Der Chat Trigger bleibt nicht öffentlich. Der MCP Client nutzt
`http://litellm:4000/mcp/neo4j`, Transport `HTTP Streamable` und den
LiteLLM-Header. n8n erhält damit ausschließlich die über LiteLLM
freigegebenen Neo4j-Tools und nie einen direkten Bolt- oder HTTP-Zugang.

Lokale Agentenmodelle können Datenmodell- und Beziehungsabsichten falsch
interpretieren, obwohl der Tool-Aufruf technisch funktioniert. Vor einer
produktiven Schreibfreigabe deshalb mit Beispieldaten testen, den Agenten auf
explizite Speicheranweisungen beschränken und einen eigenen, minimal
berechtigten Virtual Key verwenden.

Falls ein lokales Modell seine Antwort als JSON-Text ausgibt, kann ein
nachgeschalteter Code-Node den Text vereinheitlichen:

```javascript
return $input.all().map((item) => {
  const raw = item.json.output ?? "";
  try {
    const parsed = typeof raw === "string" ? JSON.parse(raw) : raw;
    return { json: { output: parsed.content ?? parsed.text ?? raw } };
  } catch {
    return { json: { output: raw } };
  }
});
```

## Wartung

```bash
cd <PROJEKT_ROOT>/Compose/n8n
docker compose ps
docker compose logs --tail=200 n8n n8n-runners n8n-postgresql
docker compose pull
docker compose up -d
```

Vor Updates die n8n-Release-Notes prüfen. `N8N_ENCRYPTION_KEY` und
`N8N_RUNNERS_AUTH_TOKEN` dürfen nicht ersetzt werden.
