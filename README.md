# Serverdienste-Dokumentation

Diese Dokumentation beschreibt die gemeinsame Serverbasis und die Docker-Compose-Stacks dieses Repositorys.

`<DOMAIN>` steht überall für die lokal konfigurierte Basisdomain.
`<PROJEKT_ROOT>` bezeichnet das Root-Verzeichnis dieses Git-Repositorys, in dem `README.md`, `.gitignore`, `Compose/` und `docs/` liegen.

Platzhalter in spitzen Klammern sind vor der Ausführung zu ersetzen. Sie sind keine gültige Shell-Syntax. Beispiel: Aus `auth.<DOMAIN>` wird mit dem Wert aus `DOMAIN=` die tatsächliche Authentik-Adresse.

Für den Ablauf der Erstinstallation: [Schnellstart](SCHNELLSTART.md). Öffentliche Adressen: [Dienste](docs/dienste.md).

## Stacks

| Stack | Enthaltene Dienste | Öffentliche Endpunkte | Vorausgesetzte Stacks | Compose-Verzeichnis |
|---|---|---|---|---|
| `core` | Traefik, Authentik Server, Authentik Worker, PostgreSQL | `https://auth.<DOMAIN>`<br>`https://proxy.<DOMAIN>/dashboard/` | Keine | `Compose/core/` |
| `partdb` | Part-DB, MariaDB | `https://partdb.<DOMAIN>` | `core` | `Compose/partdb/` |
| `ollama` | Ollama | `https://ollama.<DOMAIN>` über Traefik und Authentik | `core` | `Compose/ollama/` |
| `searxng` | SearXNG, Valkey | `https://searxng.<DOMAIN>` über Traefik und Authentik | `core` | `Compose/searxng/` |
| `jellyfin` | Jellyfin | `https://jellyfin.<DOMAIN>` über Traefik und Authentik | `core` | `Compose/jellyfin/` |
| `open-webui` | Open WebUI | `https://webui.<DOMAIN>` über Traefik und Authentik | `core`, `ollama`, `searxng` | `Compose/open-webui/` |
| `litellm` | LiteLLM Proxy | `https://litellm.<DOMAIN>/v1` und `/ui` | `core`, `ollama` | `Compose/litellm/` |

Wer SearXNG als Online-Suchwerkzeug in Open WebUI verwenden will, arbeitet die
Anleitung unter
[Open WebUI: Websuche mit SearXNG](docs/stacks/open-webui/websuche-mit-searxng.md)
ab. Eine erreichbare SearXNG-Webseite allein reicht für das Modellwerkzeug
`search_web` nicht aus.

## Installationsprinzip

Die versionierten Dateien unter `Compose/` werden bei einer normalen Installation **nicht bearbeitet**.

Installationsabhängige Daten werden stattdessen über folgende Stellen bereitgestellt:

- lokale `.env` im jeweiligen Stack-Verzeichnis,
- lokale Dateien unter `secrets/`,
- Einstellungen in den jeweiligen Dienstoberflächen.

Die Basisdomain ist frei wählbar. Feste Namen und Kennungen eines Stacks sind in seinen versionierten Dateien dokumentiert. Wer sie ändert, ändert damit die Architektur und nicht nur eine Installationsvariable.

## Empfohlene Reihenfolge

Die von oben nach unten abzuarbeitende Liste steht im [Schnellstart](SCHNELLSTART.md). Details bleiben in den jeweiligen Stack-Dokumenten.

## Dokumentation

### Allgemein

- [Dienste](docs/dienste.md)
- [Projektkonventionen](docs/projekt-konventionen.md)
- [TLS und Zertifikate](docs/tls-und-zertifikate.md)
- [Backup und Wiederherstellung](docs/backup-und-wiederherstellung.md)
- [Wartung und Updates](docs/wartung-und-updates.md)

### Server

- [Server vorbereiten](docs/server/vorbereiten.md)
- [Server konfigurieren](docs/server/konfigurieren.md)
- [Serversicherheit](docs/server/sicherheit.md)
- [Server-Fehlerbehebung](docs/server/fehlerbehebung.md)

### Stack `core`

- [Übersicht](docs/stacks/core/uebersicht.md)
- [Vorbereiten](docs/stacks/core/vorbereiten.md)
- [Erststart und Prüfung](docs/stacks/core/erststart-und-pruefung.md)
- [Authentik einrichten](docs/stacks/core/authentik-einrichten.md)
- [Authentik verwalten](docs/stacks/core/authentik-verwaltung.md)
- [Betrieb](docs/stacks/core/betrieb.md)
- [Backup und Wiederherstellung](docs/stacks/core/backup-und-wiederherstellung.md)
- [Fehlerbehebung](docs/stacks/core/fehlerbehebung.md)

### Stack `partdb`

- [Übersicht](docs/stacks/partdb/uebersicht.md)
- [Vorbereiten](docs/stacks/partdb/vorbereiten.md)
- [Authentik einrichten](docs/stacks/partdb/authentik-einrichten.md)
- [Erststart und Prüfung](docs/stacks/partdb/erststart-und-pruefung.md)
- [Verwaltung und Anwendungseinstellungen](docs/stacks/partdb/verwaltung.md)
- [Betrieb](docs/stacks/partdb/betrieb.md)
- [API, KiCad und MCP](docs/stacks/partdb/api-kicad-und-mcp.md)
- [Backup und Wiederherstellung](docs/stacks/partdb/backup-und-wiederherstellung.md)
- [Fehlerbehebung](docs/stacks/partdb/fehlerbehebung.md)

### Stack `ollama`

- [Übersicht](docs/stacks/ollama/uebersicht.md)
- [Vorbereiten](docs/stacks/ollama/vorbereiten.md)
- [Authentik einrichten](docs/stacks/ollama/authentik-einrichten.md)
- [Erststart und Prüfung](docs/stacks/ollama/erststart-und-pruefung.md)
- [Externe Python-API](docs/stacks/ollama/externe-python-api.md)
- [Betrieb](docs/stacks/ollama/betrieb.md)
- [Backup und Wiederherstellung](docs/stacks/ollama/backup-und-wiederherstellung.md)
- [Fehlerbehebung](docs/stacks/ollama/fehlerbehebung.md)

### Stack `searxng`

- [Übersicht](docs/stacks/searxng/uebersicht.md)
- [Vorbereiten](docs/stacks/searxng/vorbereiten.md)
- [Authentik einrichten](docs/stacks/searxng/authentik-einrichten.md)
- [Erststart und Prüfung](docs/stacks/searxng/erststart-und-pruefung.md)
- [Betrieb](docs/stacks/searxng/betrieb.md)
- [Backup und Wiederherstellung](docs/stacks/searxng/backup-und-wiederherstellung.md)
- [Fehlerbehebung](docs/stacks/searxng/fehlerbehebung.md)

### Stack `jellyfin`

- [Übersicht](docs/stacks/jellyfin/uebersicht.md)
- [Vorbereiten](docs/stacks/jellyfin/vorbereiten.md)
- [Authentik einrichten](docs/stacks/jellyfin/authentik-einrichten.md)
- [Erststart und Prüfung](docs/stacks/jellyfin/erststart-und-pruefung.md)
- [Betrieb](docs/stacks/jellyfin/betrieb.md)
- [Backup und Wiederherstellung](docs/stacks/jellyfin/backup-und-wiederherstellung.md)
- [Fehlerbehebung](docs/stacks/jellyfin/fehlerbehebung.md)

### Stack `open-webui`

- [Übersicht](docs/stacks/open-webui/uebersicht.md)
- [Vorbereiten](docs/stacks/open-webui/vorbereiten.md)
- [Authentik einrichten](docs/stacks/open-webui/authentik-einrichten.md)
- [Alternative ohne OIDC](docs/stacks/open-webui/authentik-einrichten-ohne-oidc.md)
- [Erststart und Prüfung](docs/stacks/open-webui/erststart-und-pruefung.md)
- [Websuche mit SearXNG](docs/stacks/open-webui/websuche-mit-searxng.md)
- [Betrieb](docs/stacks/open-webui/betrieb.md)
- [Backup und Wiederherstellung](docs/stacks/open-webui/backup-und-wiederherstellung.md)
- [Fehlerbehebung](docs/stacks/open-webui/fehlerbehebung.md)

### Stack `litellm`

- [Übersicht](docs/stacks/litellm/uebersicht.md)
- [Vorbereiten](docs/stacks/litellm/vorbereiten.md)
- [Authentik einrichten](docs/stacks/litellm/authentik-einrichten.md)
- [Erststart und Prüfung](docs/stacks/litellm/erststart-und-pruefung.md)
- [Betrieb und Clients](docs/stacks/litellm/betrieb-und-clients.md)
- [Backup und Wiederherstellung](docs/stacks/litellm/backup-und-wiederherstellung.md)
- [Fehlerbehebung](docs/stacks/litellm/fehlerbehebung.md)
