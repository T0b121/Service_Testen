# n8n-Stack: Übersicht

n8n automatisiert interne Dienste und stellt private Chat-Workflows bereit.
Die Oberfläche `https://n8n.<DOMAIN>` ist durch Authentik Forward Auth
geschützt. n8n Community unterstützt kein natives Authentik-OIDC; deshalb
bleibt der n8n-Besitzeraccount als zusätzliche lokale Anmeldung bestehen.

| Eigenschaft | Wert |
|---|---|
| Images | n8n und n8n-Runners mit derselben festgelegten Version; PostgreSQL 18 |
| Browseroberfläche | `https://n8n.<DOMAIN>` über Traefik und Authentik |
| Persistenz | PostgreSQL-Volume `n8n_postgresql_data` und `n8n_data` |
| Code-Ausführung | externer `n8n-runners`-Container; kein privilegierter n8n-Sandbox-Container |
| LLM-Zugang | LiteLLM intern über `http://litellm:4000/v1` und separaten Virtual Key |
| Suche | SearXNG intern über `http://searxng-internal:8080` |
| Graphzugang | optional ausschließlich über LiteLLM-MCP, nie per Neo4j-HTTP-Node |
| Authentik-Gruppe | `n8n-users`; `n8n-admins` für Verwaltungsberechtigungen |

Es gibt keine Host-Port-Bindungen. PostgreSQL und die Runners liegen nur im
internen Stack-Netz. n8n tritt weiteren internen Client-Netzen ausschließlich
für die tatsächlich vorgesehenen Dienste bei.

Weiter mit [Vorbereiten](vorbereiten.md).
