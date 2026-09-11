# Dienste

Diese Seite ist die zentrale Übersicht der öffentlichen Adressen und der für
andere Container vorgesehenen internen Dienstendpunkte. Einrichtung, Betrieb
und Fehlerbehebung stehen jeweils in der Dokumentation des zugehörigen Stacks.

## Öffentliche Dienste

| Dienst | Adresse | Zweck |
|---|---|---|
| Authentik | `https://auth.<DOMAIN>` | Anmeldung und Zugriffssteuerung |
| Traefik-Dashboard | `https://proxy.<DOMAIN>/dashboard/` | Proxy-Verwaltung |
| Uptime Kuma | `https://uptime.<DOMAIN>` | Überwachungsdashboard hinter Authentik und lokalem Uptime-Kuma-Login |
| Qdrant | `https://qdrant.<DOMAIN>/dashboard` | Vektordatenbank-Web-UI hinter Authentik; die Web-UI verlangt zusätzlich den lokalen Qdrant-API-Schlüssel |
| Neo4j | `https://neo4j.<DOMAIN>/browser/` | Graphdatenbank-Web-UI hinter Authentik und nativer Neo4j-Anmeldung |
| Part-DB | `https://partdb.<DOMAIN>` | Teileverwaltung |
| Ollama | `https://ollama.<DOMAIN>` | Durch Authentik geschützte Modell-API |
| Open WebUI | `https://webui.<DOMAIN>` | Browseroberfläche für Ollama hinter Authentik |
| LiteLLM | `https://litellm.<DOMAIN>/v1`<br>`https://litellm.<DOMAIN>/ui` | OpenAI-kompatible Modell-API per LiteLLM-Virtual-Key; Verwaltungsoberfläche hinter Authentik |
| SearXNG | `https://searxng.<DOMAIN>` | Metasuche hinter Authentik; internes Online-Suchwerkzeug für Open WebUI |
| Jellyfin | `https://jellyfin.<DOMAIN>` | Medienbibliothek im Browser hinter Authentik und lokaler Jellyfin-Anmeldung |
| Nextcloud | `https://cloud.<DOMAIN>` | Dateien, Kalender, Kontakte und WebDAV mit nativem Authentik-OIDC |
| ONLYOFFICE | `https://office.<DOMAIN>` | Browser-Editor für Nextcloud hinter Authentik |
| RustFS Console | `https://s3.<DOMAIN>` | S3-Objektspeicher-Konsole hinter Authentik Forward Auth und nativer OIDC-Anmeldung |
| Langfuse | `https://langfuse.<DOMAIN>` | LLM-Traces und Auswertung hinter Authentik Forward Auth und nativer OIDC-Anmeldung |
| Flowise | `https://flowise.<DOMAIN>` | Visuelle LLM-Workflows hinter Authentik Forward Auth und lokaler Flowise-Anmeldung |
| n8n | `https://n8n.<DOMAIN>` | Workflow-Automatisierung hinter Authentik Forward Auth und lokaler n8n-Anmeldung |

Für weitere öffentliche Dienste wird hier nur eine Zeile ergänzt. Die
technische Beschreibung gehört in `docs/stacks/<stack>/`.

## Interne Dienste

Diese Adressen sind ausschließlich aus Containern im jeweils genannten
Docker-Netzwerk erreichbar. Sie umgehen Traefik und damit gegebenenfalls auch
die vorgeschaltete Authentik-Anmeldung.

| Dienst | Interne Adresse | Beschreibung |
|---|---|---|
| Ollama API | `http://ollama:11434` | Direkte Modell-API im Netzwerk `web` für vertrauenswürdige Clients wie Open WebUI und LiteLLM; keine eigene API-Authentifizierung |
| LiteLLM API | `http://litellm:4000/v1` | OpenAI-kompatible API im Netzwerk `web`; ein gültiger LiteLLM-Virtual-Key bleibt erforderlich |
| SearXNG Search API | `http://searxng-internal:8080/search` | JSON-Suche im Netzwerk `searxng_clients`; keine zusätzliche Anwendungsauthentifizierung und vom SearXNG-Limiter ausgenommen |
| Qdrant REST | `http://qdrant:6333` | Vektordatenbank im Netzwerk `web` oder `qdrant_clients`; `api-key` ist erforderlich |
| Qdrant gRPC | `qdrant:6334` | gRPC für interne Vektordatenbank-Clients; `api-key` ist erforderlich |
| Neo4j Bolt | `neo4j:7687` | Graphdatenbank-Protokoll im Netzwerk `web` oder `neo4j_clients`; native Neo4j-Anmeldung erforderlich |
| RustFS S3 | `http://rustfs:9000` | S3-API nur im Netzwerk `rustfs_clients`; anwendungseigener Service-Account erforderlich |
| Langfuse Trace API | `http://langfuse:3000` | OTel-Traceaufnahme im Netzwerk `langfuse_clients`; projektbezogene Langfuse-Schlüssel erforderlich |
| n8n Health | `http://n8n:5678/healthz` | Healthcheck im Netzwerk `web`; kein allgemeiner Maschinenzugang zur n8n-Oberfläche |

Datenbanken, Cache-Dienste und reine Proxy-Ziele sind hier bewusst nicht
aufgeführt. Die Tabelle enthält nur interne Endpunkte, die andere
Anwendungs- beziehungsweise Tool-Container direkt verwenden sollen.

### Hinweise für SearXNG-Suchclients

Dienste, die SearXNG als Suchbackend verwenden, müssen dem internen
Docker-Netzwerk `searxng_clients` beitreten und die in der Tabelle angegebene
Adresse verwenden.

Das Netz ist absichtlich vom Internet getrennt und wird vom SearXNG-Stack mit
dem festen Subnetz `172.20.0.0/24` angelegt. Dieses Subnetz darf den
SearXNG-Limiter umgehen. Deshalb nur vertrauenswürdige Suchclients aufnehmen;
alle Mitglieder des Netzes können SearXNG ohne zusätzliche Anwendungsauthentik
verwenden.

Das Subnetz darf sich nicht mit einem bereits vorhandenen Docker- oder
Standortnetz überschneiden. Wird es bewusst geändert, müssen der Eintrag in
`Compose/searxng/compose.yml` und `pass_ip` in
`Compose/searxng/config/limiter.toml` exakt denselben Wert erhalten.

Die öffentliche Adresse `https://searxng.<DOMAIN>` ist dagegen für Menschen
bestimmt und verlangt Authentik Forward Auth. Sie ist kein Maschinenendpunkt
für interne Suchwerkzeuge.

Die konkrete Einrichtung für Open WebUI steht ausschließlich unter
[Open WebUI: Websuche mit SearXNG](stacks/open-webui/websuche-mit-searxng.md).
