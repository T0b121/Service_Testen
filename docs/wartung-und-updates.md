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
TRAEFIK_VERSION=3.7
AUTHENTIK_VERSION=2026.5
POSTGRES_VERSION=18
```

Diese Werte erlauben Patchupdates innerhalb der jeweiligen Linie.

Ein `docker compose pull` kann daher ein neueres Image laden, obwohl die `.env` unverändert ist.

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

## 6. Authentik

Vor Aktualisierungen:

- Release Notes der Zielversion lesen.
- Breaking Changes prüfen.
- Datenbankdump erstellen.
- `authentik_secret_key` sichern.
- PostgreSQL-Kompatibilität prüfen.
- Migrationen beim ersten Start beobachten.

Authentik verwendet keine dauerhaft gepflegte `latest`-Linie. Eine konkrete Versionslinie ist erforderlich.

## 7. Traefik

Vor Aktualisierungen:

- Migration Notes prüfen.
- neue oder veraltete Optionen kontrollieren.
- Dashboard und Forward Auth testen.
- ACME-Produktionsvolume sichern.
- Healthcheck kontrollieren.

Die aktuelle Konfiguration verwendet `trustForwardHeader=true`. Bei einem späteren Traefik-Hauptversionswechsel muss geprüft werden, ob die Option weiterhin unterstützt wird und wie vertrauenswürdige Forwarded Headers dann konfiguriert werden.

## 8. PostgreSQL

Eine PostgreSQL-Hauptversion wird nicht wie ein gewöhnliches Image-Update gewechselt.

Nicht einfach:

```dotenv
POSTGRES_VERSION=19
```

setzen und den vorhandenen Datenträger weiterverwenden.

Für einen Hauptversionswechsel wird ein dokumentiertes Upgradeverfahren benötigt, beispielsweise:

- Dump mit alter Version,
- neue leere Datenbank,
- Restore mit neuer Version,

oder:

- `pg_upgrade` nach offizieller PostgreSQL-Anleitung.

Patchupdates innerhalb derselben Hauptversion sind davon zu unterscheiden.

## 9. Rollback

Vor dem Update notieren:

- vorherige Image-Tags,
- vorherige Image-Digests,
- Backupzeitpunkt,
- geänderte `.env`,
- geänderte `compose.yml`.

Ein einfaches Zurücksetzen des Image-Tags reicht nicht immer aus, wenn bereits irreversible Datenbankmigrationen ausgeführt wurden. Deshalb ist das Backup entscheidend.

## 10. Aufräumen

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

## 11. Regelmäßige Kontrollen

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
- fehlgeschlagene Authentik-Tasks
- Datenbankgröße
- ungewöhnliche Loginereignisse
- verfügbare Sicherheitsupdates
