# Core-Stack: Backup und Wiederherstellung

Allgemeine Strategie:

- [Backup und Wiederherstellung](../../backup-und-wiederherstellung.md)

## 1. Zu sichernde Komponenten

| Komponente | Verfahren |
|---|---|
| `compose.yml` | Dateikopie |
| `.env` | verschlüsselte Dateikopie |
| `secrets/postgresql_password` | verschlüsselte Dateikopie |
| `secrets/authentik_secret_key` | verschlüsselte Dateikopie |
| PostgreSQL | `pg_dump` im Custom-Format |
| `core_authentik_data` | konsistente Volume-Sicherung |
| Produktions-ACME-Volume | konsistente Volume-Sicherung |
| Image- und Versionsinformationen | Manifest |

Das Staging-ACME-Volume ist weniger kritisch, kann aber ebenfalls gesichert werden.

## 2. Backup-Verzeichnis

```bash
cd <PROJEKT_ROOT>/Compose/core

BACKUP_TIMESTAMP="$(date -u +%Y-%m-%dT%H%M%SZ)"
BACKUP_DIR="$PWD/backups/$BACKUP_TIMESTAMP"

mkdir -p \
  "$BACKUP_DIR/configuration" \
  "$BACKUP_DIR/secrets" \
  "$BACKUP_DIR/databases" \
  "$BACKUP_DIR/volumes"
```

## 3. Manifest

```bash
{
  date -u
  hostname
  docker --version
  docker compose version
  docker compose config --images
  docker compose ps
  docker volume ls | grep core_
} > "$BACKUP_DIR/manifest.txt"
```

## 4. Konfiguration kopieren

```bash
cp compose.yml "$BACKUP_DIR/configuration/"
cp .env "$BACKUP_DIR/configuration/"
cp -a secrets/. "$BACKUP_DIR/secrets/"
```

Rechte:

```bash
chmod -R go-rwx "$BACKUP_DIR"
```

Das Backupverzeichnis enthält Klartext-Secrets und muss anschließend verschlüsselt werden.

## 5. PostgreSQL-Dump

```bash
docker compose exec -T postgresql \
  sh -c 'pg_dump \
    -U "$POSTGRES_USER" \
    -d "$POSTGRES_DB" \
    -Fc' \
  > "$BACKUP_DIR/databases/authentik.dump"
```

Lesbarkeit prüfen:

```bash
docker compose exec -T postgresql \
  pg_restore --list \
  < "$BACKUP_DIR/databases/authentik.dump" \
  >/dev/null
```

Erwartet: keine Ausgabe und Exit-Code `0`.

Dateigröße prüfen:

```bash
ls -lh "$BACKUP_DIR/databases/authentik.dump"
```

## 6. Authentik-Datenvolume sichern

Für eine konsistente Dateisicherung Server und Worker kurz stoppen:

```bash
docker compose stop \
  authentik-server \
  authentik-worker
```

Volume archivieren:

```bash
docker run --rm \
  -v core_authentik_data:/source:ro \
  -v "$BACKUP_DIR/volumes:/backup" \
  alpine:3.24 \
  tar -C /source \
      -czf /backup/core_authentik_data.tar.gz \
      .
```

Dienste wieder starten:

```bash
docker compose start \
  authentik-server \
  authentik-worker
```

Status:

```bash
docker compose ps
```

Das temporäre `alpine`-Image ist kein dauerhafter Stack-Dienst.

## 7. ACME-Volume sichern

Aktiven Volume-Namen bestimmen:

```bash
docker compose config \
  | grep -A3 'traefik_acme:'
```

Für das Produktionsvolume Traefik kurz stoppen:

```bash
docker compose stop traefik
```

Beispiel Produktion:

```bash
docker run --rm \
  -v core_traefik_acme_production:/source:ro \
  -v "$BACKUP_DIR/volumes:/backup" \
  alpine:3.24 \
  tar -C /source \
      -czf /backup/core_traefik_acme_production.tar.gz \
      .
```

Danach:

```bash
docker compose start traefik
docker compose ps
```

Bei aktivem Staging den Volume-Namen und Archivnamen entsprechend ändern.

## 8. Prüfsummen

```bash
find "$BACKUP_DIR" \
  -type f \
  ! -name checksums.sha256 \
  -print0 \
  | sort -z \
  | xargs -0 sha256sum \
  > "$BACKUP_DIR/checksums.sha256"
```

Prüfen:

```bash
cd "$BACKUP_DIR"
sha256sum -c checksums.sha256
```

Erwartet: jede Datei wird mit `OK` bestätigt.

## 9. Verschlüsseln

Das gesamte Backup mit einem geeigneten Backupwerkzeug verschlüsseln.

Kein unverschlüsseltes Backup mit `.env` und `secrets/` auf fremde Systeme kopieren.

Eine zufällige Backup-Passphrase kann erzeugt werden:

```bash
umask 077
openssl rand -base64 32 \
  | tr -d '\n' \
  > backup-encryption-password
```

Die Passphrase getrennt vom Backup speichern.

## 10. Wiederherstellung: Voraussetzungen

Benötigt:

- passendes `compose.yml`
- passende `.env`
- ursprüngliche Secrets
- PostgreSQL-Dump
- Authentik-Datenarchiv
- gegebenenfalls ACME-Archiv
- kompatible Image-Versionen

## 11. Wiederherstellungsreihenfolge

### 11.1 Stack stoppen

```bash
docker compose down
```

Nur bei einer bewusst leeren Zielinstallation alte Volumes entfernen. Vorher Namen mehrfach kontrollieren:

```bash
docker volume rm \
  core_postgresql_data \
  core_authentik_data
```

Das produktive ACME-Volume nicht löschen, wenn es nicht wiederhergestellt werden soll.

### 11.2 Konfiguration und Secrets

```bash
cp BACKUP/configuration/compose.yml .
cp BACKUP/configuration/.env .
mkdir -p secrets
cp -a BACKUP/secrets/. secrets/
chmod 600 .env secrets/*
```

### 11.3 Volumes erzeugen

```bash
docker volume create core_postgresql_data
docker volume create core_authentik_data
```

### 11.4 Authentik-Datenvolume wiederherstellen

```bash
docker run --rm \
  -v core_authentik_data:/target \
  -v /PFAD/ZUM/BACKUP/volumes:/backup:ro \
  alpine:3.24 \
  sh -c 'cd /target &&
         tar -xzf /backup/core_authentik_data.tar.gz'
```

### 11.5 PostgreSQL starten

```bash
docker compose up -d postgresql
```

Warten:

```bash
watch -n 2 docker compose ps postgresql
```

### 11.6 Datenbank wiederherstellen

```bash
docker compose exec -T postgresql \
  sh -c 'pg_restore \
    --clean \
    --if-exists \
    --no-owner \
    -U "$POSTGRES_USER" \
    -d "$POSTGRES_DB"' \
  < /PFAD/ZUM/BACKUP/databases/authentik.dump
```

### 11.7 Restliche Dienste starten

```bash
docker compose up -d
docker compose ps
```

### 11.8 Logs und Funktion

```bash
docker compose logs --tail=200
curl -k -I https://auth.<DOMAIN>
```

Dashboard und Anmeldung testen.

## 12. ACME wiederherstellen

Volume erzeugen:

```bash
docker volume create core_traefik_acme_production
```

Archiv einspielen:

```bash
docker run --rm \
  -v core_traefik_acme_production:/target \
  -v /PFAD/ZUM/BACKUP/volumes:/backup:ro \
  alpine:3.24 \
  sh -c 'cd /target &&
         tar -xzf /backup/core_traefik_acme_production.tar.gz'
```

Danach Traefik starten.

## 13. Restore-Test

Mindestens prüfen:

- alle Container healthy
- Adminanmeldung
- Benutzer und Gruppen vorhanden
- Dashboard-Provider vorhanden
- Embedded Outpost gesund
- Dashboard-Zugriff
- Authentik-Dateien vorhanden
- Zertifikat beziehungsweise ACME-Konto vorhanden
- keine wiederkehrenden Datenbankfehler
