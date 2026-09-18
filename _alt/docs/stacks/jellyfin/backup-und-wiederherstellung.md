# Jellyfin-Stack: Backup und Wiederherstellung

## Backup-Umfang

| Daten | Speicherort | Bewertung |
|---|---|---|
| Jellyfin-Konfiguration, Benutzer, Datenbank und Metadaten | `jellyfin_config` | erforderlich |
| Transcoding- und Laufzeitcache | `jellyfin_cache` | optional |
| Medien | `jellyfin_media` | separat; später durch Nextcloud sichern |
| Authentik-Anwendung, Provider und Gruppenbindung | Core-Stack-Backup | erforderlich |

Das allgemeine Vorgehen steht unter
[Backup und Wiederherstellung](../../backup-und-wiederherstellung.md).

## Konfiguration sichern

```bash
cd <PROJEKT_ROOT>/Compose/jellyfin
test -n "${BACKUP_DIR:-}" || { echo 'BACKUP_DIR ist nicht gesetzt' >&2; exit 1; }
umask 077
mkdir -p "$BACKUP_DIR/configuration" "$BACKUP_DIR/volumes"
cp .env "$BACKUP_DIR/configuration/.env"

docker compose stop jellyfin
docker run --rm \
  -v jellyfin_config:/source:ro \
  -v "$BACKUP_DIR/volumes:/backup" \
  alpine:3.22 \
  tar -C /source -czf /backup/jellyfin_config.tar.gz .
docker compose start jellyfin
```

`jellyfin_cache` kann bei Bedarf nach demselben Muster gesichert werden, ist
aber für eine Wiederherstellung nicht nötig. `jellyfin_media` gehört nicht in
dieses Stack-Backup, weil es später durch Nextcloud verwaltet und gesichert
wird.

## Wiederherstellung

Auf einer neuen Zielinstallation darf das Beispiel nur verwendet werden, wenn
`jellyfin_config` noch nicht existiert:

```bash
cd <PROJEKT_ROOT>/Compose/jellyfin
test -n "${BACKUP_DIR:-}" || { echo 'BACKUP_DIR ist nicht gesetzt' >&2; exit 1; }
docker compose down
if docker volume inspect jellyfin_config >/dev/null 2>&1; then
  echo 'Volume jellyfin_config existiert bereits; Restore-Ziel zuerst bewusst klären.' >&2
  exit 1
fi
docker volume create jellyfin_config
docker run --rm \
  -v jellyfin_config:/target \
  -v "$BACKUP_DIR/volumes:/backup:ro" \
  alpine:3.22 \
  tar -C /target -xzf /backup/jellyfin_config.tar.gz
docker compose up -d
docker compose ps
```

Danach Authentik-Zugang, lokales Jellyfin-Administratorkonto und
Bibliothekskonfiguration prüfen. Das Medienvolume wird separat wiederhergestellt
beziehungsweise später durch Nextcloud bereitgestellt.
