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

`BACKUP_DIR` wie in der projektweiten
[Backup-Strategie](../../backup-und-wiederherstellung.md#4-zeitstempel-und-arbeitsvariablen)
setzen. Dann Konfiguration und Volume konsistent sichern:

```bash
cd <PROJEKT_ROOT>/Compose/open-webui
test -n "${BACKUP_DIR:-}" || { echo 'BACKUP_DIR ist nicht gesetzt' >&2; exit 1; }
umask 077
mkdir -p "$BACKUP_DIR/configuration" "$BACKUP_DIR/secrets" "$BACKUP_DIR/volumes"

cp .env "$BACKUP_DIR/configuration/.env"
cp secrets/openwebui_secret_key "$BACKUP_DIR/secrets/openwebui_secret_key"

docker compose stop open-webui

docker run --rm \
  -v openwebui_data:/source:ro \
  -v "$BACKUP_DIR/volumes:/backup" \
  alpine:3.22 \
  tar -C /source -czf /backup/openwebui_data.tar.gz .

docker compose start open-webui
```

Das Backup enthält Klartext-Secrets und muss anschließend verschlüsselt werden.

## 3. Wiederherstellung

1. Core-Stack einschließlich Authentik wiederherstellen, falls die
   Authentik-Konfiguration fehlt.
2. Ollama- und SearXNG-Stack sowie die Netzwerke `web` und
   `searxng_clients` prüfen.
3. Lokale `.env` und `secrets/openwebui_secret_key` mit Modus `600`
   bereitstellen.
4. Volume `openwebui_data` wiederherstellen.
5. Stack in der gewählten Betriebsart starten sowie Anmeldung,
   Administratorrolle und Modellverbindung prüfen.

Auf einer neuen Zielinstallation darf das folgende Beispiel nur verwendet
werden, wenn `openwebui_data` noch nicht existiert. Es bricht bei einem
vorhandenen Volume absichtlich ab:

```bash
cd <PROJEKT_ROOT>/Compose/open-webui
test -n "${BACKUP_DIR:-}" || { echo 'BACKUP_DIR ist nicht gesetzt' >&2; exit 1; }
docker compose down
if docker volume inspect openwebui_data >/dev/null 2>&1; then
  echo 'Volume openwebui_data existiert bereits; Restore-Ziel zuerst bewusst klären.' >&2
  exit 1
fi
docker volume create openwebui_data
docker run --rm \
  -v openwebui_data:/target \
  -v "$BACKUP_DIR/volumes:/backup:ro" \
  alpine:3.22 \
  tar -C /target -xzf /backup/openwebui_data.tar.gz
docker compose up -d
```

Bei der Forward-Auth-Alternative zusätzlich `compose.local-auth.yml` für
alle Compose-Befehle verwenden. Bei der OIDC-Standardkonfiguration das
Rollen-Scope-Mapping `Open WebUI Rollen` wiederherstellen und die OIDC-
Zugangsdaten in `.env` bereitstellen.
