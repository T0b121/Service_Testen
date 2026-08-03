# Open-WebUI-Stack: Backup und Wiederherstellung

## 1. Backup-Umfang

| Daten | Speicherort | Bewertung |
|---|---|---|
| Open-WebUI-Datenbank, OIDC-Konten, Dateien und Einstellungen | Volume `openwebui_data` | erforderlich |
| Session- und Anwendungssignierschlüssel | `secrets/openwebui_secret_key` | erforderlich, verschlüsselt sichern |
| OIDC-Provider, Rollen-Scope-Mapping, Gruppen und Bindings | Authentik-PostgreSQL-Backup des Core-Stacks | erforderlich |
| OIDC-Client-ID und -Secret | lokale Datei `.env` | erforderlich, verschlüsselt sichern |
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

1. Core-Stack einschließlich Authentik wiederherstellen, falls die OIDC-
   Konfiguration fehlt.
2. Ollama-Stack und Netzwerk `web` prüfen.
3. Lokale `.env` und `secrets/openwebui_secret_key` mit Modus `600`
   bereitstellen.
4. Volume `openwebui_data` wiederherstellen.
5. Stack starten sowie OIDC-Anmeldung, Administratorrolle und Modellverbindung
   prüfen.
