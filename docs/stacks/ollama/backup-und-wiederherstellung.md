# Ollama-Stack: Backup und Wiederherstellung

## 1. Backup-Umfang

| Daten | Speicherort | Bewertung |
|---|---|---|
| Ollama-Modelle, Manifeste und Dienstschlüssel | Volume `ollama_data` | optional; Modelle können erneut geladen werden, ein Volume-Backup verschlüsseln |
| Version und Modellliste | lokale Dokumentation oder Backup-Manifest | empfohlen |
| Zugriffsgruppen und Provider | Authentik-PostgreSQL-Backup des Core-Stacks | erforderlich für die äußere Zugriffskontrolle |

Für Testmodelle genügt meist die dokumentierte Modellliste. Ein vollständiges
Volume-Backup kann sehr groß werden und enthält den von Ollama beim ersten
Start erzeugten privaten Dienstschlüssel. Es wird verschlüsselt gesichert und
nicht in Git abgelegt.

## 2. Modellliste sichern

```bash
cd <PROJEKT_ROOT>/Compose/ollama
docker compose exec ollama ollama list
```

Die Ausgabe nicht blind in Git ablegen; sie kann in einem verschlüsselten
Backup-Manifest gespeichert werden.

## 3. Volume sichern

`BACKUP_DIR` wie in der projektweiten
[Backup-Strategie](../../backup-und-wiederherstellung.md#4-zeitstempel-und-arbeitsvariablen)
setzen. Vor einer konsistenten Sicherung den Stack anhalten und das Volume
archivieren:

```bash
cd <PROJEKT_ROOT>/Compose/ollama
test -n "${BACKUP_DIR:-}" || { echo 'BACKUP_DIR ist nicht gesetzt' >&2; exit 1; }
umask 077
mkdir -p "$BACKUP_DIR/configuration" "$BACKUP_DIR/volumes"
cp .env "$BACKUP_DIR/configuration/.env"

docker compose stop ollama

docker run --rm \
  -v ollama_data:/source:ro \
  -v "$BACKUP_DIR/volumes:/backup" \
  alpine:3.22 \
  tar -C /source -czf /backup/ollama_data.tar.gz .

docker compose start ollama
```

Das Archiv enthält den privaten Ollama-Dienstschlüssel und muss verschlüsselt
gespeichert werden.

## 4. Wiederherstellung

Reihenfolge:

1. Core-Stack und Authentik wiederherstellen, falls deren Konfiguration fehlt.
2. `web`-Netzwerk prüfen.
3. Ollama-Stack mit derselben `.env` bereitstellen.
4. `ollama_data` aus dem Backup wiederherstellen oder benötigte Modelle neu laden.
5. Gruppenbindung in Authentik und externen Zugriff prüfen.

Auf einer neuen Zielinstallation darf das folgende Beispiel nur verwendet
werden, wenn `ollama_data` noch nicht existiert:

```bash
cd <PROJEKT_ROOT>/Compose/ollama
test -n "${BACKUP_DIR:-}" || { echo 'BACKUP_DIR ist nicht gesetzt' >&2; exit 1; }
docker compose down
if docker volume inspect ollama_data >/dev/null 2>&1; then
  echo 'Volume ollama_data existiert bereits; Restore-Ziel zuerst bewusst klären.' >&2
  exit 1
fi
docker volume create ollama_data
docker run --rm \
  -v ollama_data:/target \
  -v "$BACKUP_DIR/volumes:/backup:ro" \
  alpine:3.22 \
  tar -C /target -xzf /backup/ollama_data.tar.gz
docker compose up -d
```

Danach mindestens ausführen:

```bash
docker compose ps
docker compose exec ollama ollama list
```
