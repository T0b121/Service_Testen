# n8n-Stack: Fehlerbehebung

## `Redirect URI Error` bei Authentik

Beim Provider **n8n Access Provider** External Host und beide Callback-URIs
aus [Authentik einrichten](authentik-einrichten.md) exakt prüfen. Danach
Browser-Cookies löschen oder ein privates Fenster verwenden.

## `Could not connect to your MCP server` oder `Authentication failed`

Der MCP Client muss `http://litellm:4000/mcp/neo4j` mit `HTTP Streamable`
verwenden. Das Header-Credential braucht exakt:

```text
Authorization: Bearer sk-...
```

Die LiteLLM-Key-ID, ein n8n-interner Credential-Wert oder ein Header
`x-litellm-api-key` sind an diesem MCP-Gateway nicht ausreichend. Der
Virtual-Key benötigt zudem die explizite MCP-Serverfreigabe.

## Modell antwortet leer oder ruft keine Tools auf

Für lokale Agentenmodelle in LiteLLM Provider **Ollama Chat** statt
**Ollama** verwenden und `supports_function_calling` im Model Info setzen.
Der normale Ollama-Provider ist für einfache Textgenerierung geeignet, aber
nicht die korrekte Wahl für n8n-Agenten mit nativen Tools.

Prüfen, ob der MCP Client im Workflow wirklich als gestrichelte
`ai_tool`-Verbindung am AI Agent hängt. Ein erfolgreicher Chat ohne Tool-Call
beweist nur die Modellverbindung, nicht den Datenbankzugriff.

## Runners oder Code-Nodes funktionieren nicht

```bash
cd <PROJEKT_ROOT>/Compose/n8n
docker compose ps
docker compose logs --tail=200 n8n n8n-runners
```

`N8N_RUNNERS_AUTH_TOKEN` muss in n8n und n8n-runners exakt gleich sein. Die
Runners sind kein Docker-Sandbox-Ersatz und benötigen keine Docker-Socket- oder
Privileged-Berechtigung.
