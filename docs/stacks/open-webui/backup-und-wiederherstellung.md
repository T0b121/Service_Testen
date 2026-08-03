# Open-WebUI-Stack: Backup und Wiederherstellung

## 1. Backup-Umfang

| Daten | Speicherort | Bewertung |
|---|---|---|
| Open-WebUI-Datenbank, Benutzerkonten, Dateien und Einstellungen | Volume `openwebui_data` | erforderlich |
| Session- und Anwendungssignierschlüssel | `secrets/openwebui_secret_key` | erforderlich, verschlüsselt sichern |
| Authentik-Anwendung, Provider, Gruppen und Bindings | Authentik-PostgreSQL-Backup des Core-Stacks | erforderlich |
| OIDC-Client-ID und -Secret | lokale Datei `.env` | für die OIDC-Standardkonfiguration erforderlich, verschlüsselt sichern |
| Modelle | Volume `ollama_data` des Ollama-Stacks | separat nach Ollama-Strategie |

Das Secret und das Volume gehören nicht in Git. Ohne den Signierschlüssel
werden bestehende Sitzungen ungültig.

## 2. Volume sichern

```bash
cd <PROJEKT_ROOT>/Compose/open-webui
docker compose stop open-webui
```

`openwebui_data` außerhalb des Repositorys nach der projektweiten
[Backup-Strategie](../../backup-und-wiederherstellung.md) sichern. Die
Secret-Datei nur in ein verschlüsseltes Backup aufnehmen. Danach:

```bash
docker compose up -d
```

## 3. Wiederherstellung

1. Core-Stack einschließlich Authentik wiederherstellen, falls die
   Authentik-Konfiguration fehlt.
2. Ollama-Stack und Netzwerk `web` prüfen.
3. Lokale `.env` und `secrets/openwebui_secret_key` mit Modus `600`
   bereitstellen.
4. Volume `openwebui_data` wiederherstellen.
5. Stack in der gewählten Betriebsart starten sowie Anmeldung,
   Administratorrolle und Modellverbindung prüfen.

Bei der Forward-Auth-Alternative zusätzlich `compose.local-auth.yml` für
alle Compose-Befehle verwenden. Bei der OIDC-Standardkonfiguration das
Rollen-Scope-Mapping `Open WebUI Rollen` wiederherstellen und die OIDC-
Zugangsdaten in `.env` bereitstellen.
