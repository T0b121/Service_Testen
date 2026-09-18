# Dienste auf einen Blick

Pro Stack gibt es genau eine kompakte Seite: Zweck, erste Nutzung, wichtige
Einstellungen, Daten und häufige Probleme. Zusatzdienste wie PostgreSQL, Redis,
Runner und OnlyOffice sind auf der Seite ihres jeweiligen Stacks erklärt.

## Gemeinsamer Einstieg

- [Schnellstart](../SCHNELLSTART.md) für die einmalige Vorbereitung und das Menü.
- [Manager](manager.md) für Konfiguration, Hooks und Nutzerverwaltung.
- [Betriebsprüfungen](validierung.md) für die noch ausstehenden Live-Tests.

Benutzer und Dienstgruppen ausschließlich im Manager ändern. So laufen die
lokalen Anwendungshooks mit; ein periodischer GitLab-Synchronisationsdienst ist
nicht vorgesehen. Open WebUI verwendet ausschließlich SSO. Andere Stacks haben
nur dort natives SSO, wo es in ihrer jeweiligen Seite beschrieben ist.

## Stacks

| Dienst | Wofür? |
|---|---|
| [ComfyUI](stacks/comfyui.md) | ComfyUI ist ein grafischer Editor für KI-Workflows, beispielsweise zur Bildgenerierung. |
| [Core: Traefik und Authentik](stacks/core.md) | Core ist die gemeinsame Eingangstür für die anderen Stacks. |
| [Flowise](stacks/flowise.md) | Flowise erstellt KI-Abläufe über einen visuellen Node-Editor. |
| [GitLab](stacks/gitlab.md) | GitLab verwaltet Git-Repositories, Issues und Merge Requests. |
| [Jellyfin](stacks/jellyfin.md) | Jellyfin verwaltet eine persönliche Medienbibliothek und spielt deren Inhalte ab. |
| [Langfuse](stacks/langfuse.md) | Langfuse hilft beim Beobachten und Auswerten von LLM-Anwendungen. |
| [LiteLLM](stacks/litellm.md) | LiteLLM ist das gemeinsame API-Gateway für Modellzugriffe. |
| [LocalAI](stacks/localai.md) | LocalAI stellt lokal betriebene KI-Modelle über APIs bereit. |
| [n8n](stacks/n8n.md) | n8n verbindet Dienste zu automatisierten Workflows. |
| [Neo4j](stacks/neo4j.md) | Neo4j ist eine Graphdatenbank für Knoten, Beziehungen und ihre Eigenschaften. |
| [Nextcloud und OnlyOffice](stacks/nextcloud.md) | Nextcloud stellt Dateien, Freigaben und weitere Cloud-Funktionen im Browser bereit. |
| [Ollama](stacks/ollama.md) | Ollama führt lokal installierte Sprachmodelle aus. |
| [Open WebUI](stacks/open-webui.md) | Open WebUI ist die Browseroberfläche für Gespräche mit Sprachmodellen. |
| [Paperless-ngx](stacks/paperless.md) | Paperless-ngx archiviert Dokumente und macht deren Inhalte durchsuchbar. |
| [Part-DB](stacks/partdb.md) | Part-DB verwaltet elektronische Bauteile und deren Lagerbestand. |
| [Qdrant](stacks/qdrant.md) | Qdrant speichert Vektoren und zugehörige Metadaten. |
| [RustFS](stacks/rustfs.md) | RustFS stellt S3-kompatiblen Objektspeicher bereit. |
| [SearXNG](stacks/searxng.md) | SearXNG bündelt Suchanfragen an mehrere Suchmaschinen. |
| [Uptime Kuma](stacks/uptime-kuma.md) | Uptime Kuma überwacht die Erreichbarkeit von Diensten. |

## Was gilt für alle Seiten?

`<DOMAIN>` ist die im Manager gewählte Basisdomain. Öffentliche Anwendungsrouten
liegen hinter Forward Auth; externe API-Clients und Webhooks müssen damit
zurechtkommen. Interne Verbindungen brauchen passende Netze und Dienst-Credentials.

Die Texte beschreiben den aktiven Ordner `compose/`. `_alt/` bleibt ein Archiv
und ist keine aktuelle Einrichtungsanleitung. Alte Volumes werden nicht automatisch
übernommen. Für Export, Import und Sicherungszeitpläne das Manager-Menü verwenden.
