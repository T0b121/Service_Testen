# Flowise-Stack: Übersicht

Flowise ist eine visuelle Oberfläche zum Zusammenstellen von LLM-Workflows,
RAG-Pipelines und Agenten. Die Browseroberfläche ist unter
`https://flowise.<DOMAIN>` verfügbar. Die Anwendung verwendet PostgreSQL
anstelle der früheren lokalen SQLite-Datenbank.

| Eigenschaft | Wert |
|---|---|
| Images | Flowise `3.1.3`, PostgreSQL `18` |
| Browseroberfläche | `https://flowise.<DOMAIN>` über Traefik und Authentik Forward Auth |
| Anwendungsanmeldung | lokaler Flowise-Account zusätzlich zu Forward Auth |
| LLM-Zugang | LiteLLM intern über `http://litellm:4000/v1` |
| Vektorspeicher | Qdrant intern über `http://qdrant:6333` im Netz `qdrant_clients` |
| Graphdatenbank | Neo4j intern über `neo4j://neo4j:7687` im Netz `neo4j_clients` |
| Persistenz | PostgreSQL-Volume `flowise_postgresql_data` und externes Volume `flowise_data` |
| Authentik-Gruppe | `flowise-users`; `flowise-admins` ist für spätere Verwaltungsrollen reserviert |

Es gibt keine Host-Port-Bindungen. PostgreSQL ist ausschließlich im internen
Stack-Netz erreichbar. Flowise Community bietet kein natives OIDC; daher
schützt Authentik den Browserzugriff per Forward Auth, während Flowise seine
eigene Benutzerverwaltung verwendet.

Weiter mit [Vorbereiten](vorbereiten.md).
