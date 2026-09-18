# SearXNG-Stack: Backup und Wiederherstellung

SearXNG selbst speichert keine Benutzer- oder Suchhistorie. Für einen
funktionsfähigen Restore sind die lokale `.env` und die versionierte
Konfiguration maßgeblich. Die beiden Volumes enthalten nur optional
wiederherstellbare Cache- und Limiter-Zustände:

| Bestandteil | Inhalt | Für Restore erforderlich |
|---|---|---|
| `.env` | Domain, Image-Tags und `SEARXNG_SECRET` | Ja |
| `config/settings.yml` und `config/limiter.toml` | versionierte SearXNG-Einstellungen | Ja, aus dem Repository |
| `searxng_cache` | Favicon- und Laufzeitcache | Nein |
| `searxng_valkey_data` | Valkey-Daten des Rate-Limiters | Nein |

Das grundlegende Vorgehen steht in
[Backup und Wiederherstellung](../../backup-und-wiederherstellung.md).

## Konfiguration und optionalen Cache sichern

```bash
cd <PROJEKT_ROOT>/Compose/searxng
test -n "${BACKUP_DIR:-}" || { echo 'BACKUP_DIR ist nicht gesetzt' >&2; exit 1; }
umask 077
mkdir -p "$BACKUP_DIR/configuration" "$BACKUP_DIR/volumes"
cp .env "$BACKUP_DIR/configuration/.env"
cp -a config "$BACKUP_DIR/configuration/"

docker compose stop searxng

docker run --rm \
  -v searxng_cache:/source:ro \
  -v "$BACKUP_DIR/volumes:/backup" \
  alpine:3.22 \
  tar -C /source -czf /backup/searxng_cache.tar.gz .

docker compose start searxng
```

Das Valkey-Volume enthält ebenfalls nur flüchtige Daten. Es kann mit demselben
Muster gesichert werden, wenn eine vollständige Momentaufnahme erwünscht ist.

Die Konfigurationskopie enthält `SEARXNG_SECRET` im Klartext. Das gesamte
Backup deshalb verschlüsseln und außerhalb des Repositorys speichern.

## Wiederherstellung

1. Stack-Dateien derselben oder einer kompatiblen Version bereitstellen.
2. `.env` einschließlich des unveränderten `SEARXNG_SECRET` wiederherstellen.
3. Optional das Cache- und Valkey-Volume zurückspielen.
4. Mit `docker compose up -d` starten und die Prüfungen aus
   [Erststart und Prüfung](erststart-und-pruefung.md) ausführen.
