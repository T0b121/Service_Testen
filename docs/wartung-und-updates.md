# Wartung und Updates

## 1. Grundsatz

Updates werden kontrolliert durchgeführt:

1. Release Notes lesen.
2. Kompatibilität prüfen.
3. Backup erstellen.
4. aktuelle Versionen und Digests dokumentieren.
5. Images laden.
6. Konfiguration validieren.
7. Dienste neu erstellen.
8. Healthchecks und Logs prüfen.
9. Funktionstest durchführen.
10. Rollbackbereitschaft behalten.

## 2. Versionslinien

Beispiel:

```dotenv
DIENST_VERSION=<VERSION>
```

Ob ein Wert Patchupdates erlaubt, hängt vom verwendeten Tag ab. Ein
Versionslinientag wie `3.7` kann beim nächsten `docker compose pull` ein neues
`3.7.x`-Image laden. Ein vollständiger Tag wie `v1.95.0` oder
`2026.8.4-c63835bd2` bleibt dagegen unverändert, bis er bewusst in `.env`
angepasst wird.

Aktuelle Image-IDs dokumentieren:

```bash
docker compose images
```

Digests:

```bash
docker image inspect \
  --format '{{index .RepoDigests 0}}' \
  IMAGE
```

## 3. Vor dem Update

Im Stack-Verzeichnis:

```bash
docker compose config --quiet
docker compose ps
docker compose images
docker compose logs --tail=100
```

Danach das stack-spezifische Backup ausführen.

Freien Speicher prüfen:

```bash
df -h
docker system df
```

## 4. Images laden

```bash
docker compose pull
```

Der laufende Container wird dadurch noch nicht ersetzt.

Prüfen:

```bash
docker compose images
```

## 5. Update anwenden

```bash
docker compose up -d
```

Bei Bedarf einen einzelnen Dienst ausdrücklich neu erstellen:

```bash
docker compose up -d --force-recreate <dienst>
```

Danach:

```bash
docker compose ps
docker compose logs --tail=150
```

## 6. Stack-spezifische Hinweise

Zusätzliche Prüfungen, Datenbankmigrationen und Funktionschecks werden ausschließlich in den Stack-Dokumenten gepflegt:

- [Core: Betrieb](stacks/core/betrieb.md)
- [Part-DB: Betrieb](stacks/partdb/betrieb.md)
- [Ollama: Betrieb](stacks/ollama/betrieb.md)
- [Open WebUI: Betrieb](stacks/open-webui/betrieb.md)
- [LiteLLM: Betrieb und Clients](stacks/litellm/betrieb-und-clients.md)
- [SearXNG: Betrieb](stacks/searxng/betrieb.md)
- [Jellyfin: Betrieb](stacks/jellyfin/betrieb.md)

## 7. Rollback

Vor dem Update notieren:

- vorherige Image-Tags,
- vorherige Image-Digests,
- Backupzeitpunkt,
- geänderte `.env`,
- verwendeter Git-Commit und bewusst versionierte Stackänderungen.

Ein einfaches Zurücksetzen des Image-Tags reicht nicht immer aus, wenn bereits irreversible Datenbankmigrationen ausgeführt wurden. Deshalb ist das Backup entscheidend.

## 8. Aufräumen

Nicht mehr benötigte Images anzeigen:

```bash
docker image ls
```

Vorsichtig bereinigen:

```bash
docker image prune
```

Keine Volumes automatisch löschen:

```bash
# Nicht als normale Wartung verwenden:
docker volume prune
docker system prune --volumes
```

Vor jeder Bereinigung prüfen, ob alte Images für ein Rollback benötigt werden.

## 9. Regelmäßige Kontrollen

```bash
docker compose ps
docker compose logs --since=24h
docker system df
df -h
sudo systemctl --failed
```

Zusätzlich:

- Zertifikatsablauf
- Backupalter
- Restore-Test
- verfügbare Sicherheitsupdates
