# Part-DB-Stack: Backup und Wiederherstellung

Allgemeine Strategie:

- [Backup und Wiederherstellung](../../backup-und-wiederherstellung.md)

Part-DB selbst dokumentiert als wesentliche Bestandteile Datenbank, `uploads/` und `public/media/`. In diesem Projekt kommen zusätzlich die lokale `.env` und die installationsspezifischen Secret-Dateien hinzu.

## 1. Zu sichernde Komponenten

| Komponente | Verfahren |
|---|---|
| versionierte `compose.yml`, `config/`, `scripts/` | über Git und optional Dateikopie im Backup |
| `.env` | verschlüsselte Dateikopie |
| `secrets/partdb_app_secret` | verschlüsselte Dateikopie |
| `secrets/mariadb_password` | verschlüsselte Dateikopie |
| `secrets/mariadb_root_password` | verschlüsselte Dateikopie |
| `secrets/authentik_saml_idp_certificate` | Dateikopie; trotzdem mit dem Secret-Satz sichern |
| `secrets/partdb_saml_sp_certificate` | Dateikopie |
| `secrets/partdb_saml_sp_private_key` | verschlüsselte Dateikopie |
| MariaDB | konsistenter SQL-Dump |
| `partdb_uploads` | konsistente Volume-Sicherung |
| `partdb_public_media` | konsistente Volume-Sicherung |
| Image-Versionen und Digests | Manifest |
| Authentik-Konfiguration | über das Backup des Core-Stacks |

Der private SAML-SP-Schlüssel, Datenbankpasswörter und Anwendungssecret dürfen nicht verloren gehen oder unverschlüsselt extern gespeichert werden.

## 2. Cross-Stack-Abhängigkeit zu Authentik

Ein vollständiger Wiederanlauf von Part-DB benötigt zusätzlich die Authentik-Seite der Konfiguration:

- Gruppen `partdb-admin`, `partdb-editor`, `partdb-readonly`,
- `Part-DB Access`,
- `Part-DB SSO`,
- SAML-Property-Mapping,
- Zertifikatsobjekte,
- Benutzer- und Gruppenmitgliedschaften.

Diese Daten liegen im Core-Stack beziehungsweise in Authentiks PostgreSQL-Datenbank und werden durch [Core: Backup und Wiederherstellung](../core/backup-und-wiederherstellung.md) gesichert.

Ein Part-DB-Backup alleine ist daher für einen vollständigen Neuaufbau des gesamten SSO-Systems nicht ausreichend.

## 3. Backup außerhalb des Git-Repositorys anlegen

Backups enthalten lokale `.env`, Secrets und Nutzdaten. Sie werden deshalb **außerhalb** von `<PROJEKT_ROOT>` erstellt.

Beispiel:

```bash
cd <PROJEKT_ROOT>/Compose/partdb

BACKUP_TIMESTAMP="$(date -u +%Y-%m-%dT%H%M%SZ)"
BACKUP_ROOT="$HOME/serverdienste-backups/partdb"
BACKUP_DIR="$BACKUP_ROOT/$BACKUP_TIMESTAMP"

umask 077
mkdir -p \
  "$BACKUP_DIR/configuration" \
  "$BACKUP_DIR/secrets" \
  "$BACKUP_DIR/databases" \
  "$BACKUP_DIR/volumes"

chmod 700 "$BACKUP_ROOT" "$BACKUP_DIR"
```

So ist das Backup nicht davon abhängig, dass zusätzliche Backup-Muster in `.gitignore` vorhanden sind.

## 4. Manifest erstellen

```bash
{
  date -u
  hostname
  docker --version
  docker compose version
  docker compose config --images
  docker compose ps
  docker volume ls | grep -E 'partdb_(uploads|public_media|mariadb_data)'
} > "$BACKUP_DIR/manifest.txt"
```

Optional zusätzlich Git-Stand dokumentieren:

```bash
cd <PROJEKT_ROOT>
git rev-parse HEAD >> "$BACKUP_DIR/manifest.txt"
cd Compose/partdb
```

## 5. Konfiguration und Secrets kopieren

```bash
cp .env "$BACKUP_DIR/configuration/"
cp compose.yml "$BACKUP_DIR/configuration/"
cp -a config "$BACKUP_DIR/configuration/"
cp -a scripts "$BACKUP_DIR/configuration/"
cp -a secrets/. "$BACKUP_DIR/secrets/"

chmod -R go-rwx "$BACKUP_DIR"
```

Die Kopien von `compose.yml`, `config/` und `scripts/` sind für die Wiederherstellung praktisch, obwohl sie zusätzlich in Git vorhanden sind.

## 6. MariaDB-Dump erstellen

Der Dump wird aus dem laufenden MariaDB-Container erstellt. Das Passwort wird aus dem bereits eingehängten Docker-Secret gelesen und für den Client kurzzeitig in eine Datei mit Modus `600` geschrieben. Dadurch erscheint es weder in der Shell-History noch als Passwortargument in der Prozessliste.

```bash
docker compose exec -T mariadb sh -c '
  CLIENT_CNF="$(mktemp)"
  trap "rm -f \"$CLIENT_CNF\"" EXIT HUP INT TERM
  chmod 600 "$CLIENT_CNF"

  {
    printf "[client]\nuser=%s\npassword=" "$MARIADB_USER"
    cat /run/secrets/mariadb_password
    printf "\n"
  } > "$CLIENT_CNF"

  mariadb-dump \
    --defaults-extra-file="$CLIENT_CNF" \
    --single-transaction \
    --quick \
    --skip-lock-tables \
    "$MARIADB_DATABASE"
' > "$BACKUP_DIR/databases/partdb.sql"
```

`--defaults-extra-file` steht absichtlich als erste Clientoption. Die temporäre Datei wird durch `trap` auch beim normalen Programmende wieder entfernt.

Prüfen:

```bash
test -s "$BACKUP_DIR/databases/partdb.sql"
wc -c "$BACKUP_DIR/databases/partdb.sql"
```

Erwartet: Datei ist nicht leer. Die Dumpdatei enthält Anwendungsdaten und wird nicht in Supportausgaben veröffentlicht.

`--single-transaction` erzeugt für transaktionale Tabellen einen konsistenten Datenbankstand, ohne das MariaDB-Dateivolume blind zu kopieren.

## 7. Dateivolumes konsistent sichern

Nach dem Datenbankdump Part-DB kurz stoppen, damit während der Dateisicherung keine Uploads oder Medien geändert werden:

```bash
docker compose stop partdb
```

MariaDB bleibt für diesen Schritt laufen.

### Uploads

```bash
docker run --rm \
  -v partdb_uploads:/source:ro \
  -v "$BACKUP_DIR/volumes:/backup" \
  alpine:3.24 \
  tar -C /source \
      -czf /backup/partdb_uploads.tar.gz \
      .
```

### Öffentliche Medien

```bash
docker run --rm \
  -v partdb_public_media:/source:ro \
  -v "$BACKUP_DIR/volumes:/backup" \
  alpine:3.24 \
  tar -C /source \
      -czf /backup/partdb_public_media.tar.gz \
      .
```

Part-DB wieder starten:

```bash
docker compose start partdb
docker compose ps
```

## 8. Sicherungen prüfen

```bash
ls -lh \
  "$BACKUP_DIR/databases/partdb.sql" \
  "$BACKUP_DIR/volumes/partdb_uploads.tar.gz" \
  "$BACKUP_DIR/volumes/partdb_public_media.tar.gz"
```

Archive testweise lesen:

```bash
tar -tzf "$BACKUP_DIR/volumes/partdb_uploads.tar.gz" >/dev/null
tar -tzf "$BACKUP_DIR/volumes/partdb_public_media.tar.gz" >/dev/null
```

Erwartet: keine Fehler.

## 9. Prüfsummen erstellen

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

Jede Datei muss mit `OK` bestätigt werden.

## 10. Backup verschlüsseln

Das Backup enthält unter anderem:

- Datenbankinhalt,
- Benutzer- und Bestandsdaten,
- Passwörter,
- privaten SAML-Schlüssel,
- `APP_SECRET`.

Es muss vor externer Speicherung oder Übertragung mit einem geeigneten Backupwerkzeug verschlüsselt werden. Siehe [allgemeine Backupstrategie](../../backup-und-wiederherstellung.md).

Kein unverschlüsseltes Backupverzeichnis dauerhaft in Cloudspeicher oder auf fremde Systeme kopieren.

## 11. Wiederherstellung: Grundsatz

Für einen Restore zuerst die **gleiche beziehungsweise kompatible Part-DB- und MariaDB-Version** verwenden, mit der das Backup erstellt wurde.

Nicht gleichzeitig einen Restore und ein Versionsupgrade durchführen. Erst den alten Stand erfolgreich wiederherstellen und testen, danach separat aktualisieren.

Benötigt:

- passender Git-Stand beziehungsweise die gesicherten versionierten Dateien,
- ursprüngliche `.env`,
- ursprüngliche Secrets,
- MariaDB-Dump,
- beide Dateivolume-Archive,
- funktionierender Core-Stack,
- bei vollständigem Systemrestore auch ein passendes Core-/Authentik-Backup.

## 12. Zielinstallation vorbereiten

Im Part-DB-Verzeichnis:

```bash
cd <PROJEKT_ROOT>/Compose/partdb

docker compose down
```

Lokale Konfiguration und Secrets aus dem entschlüsselten Backup zurückspielen:

```bash
cp <BACKUP_DIR>/configuration/.env .
mkdir -p secrets
cp -a <BACKUP_DIR>/secrets/. secrets/
chmod 600 .env secrets/*
```

Versionierte Dateien bevorzugt über den im Manifest dokumentierten Git-Stand wiederherstellen. Damit bleiben `compose.yml`, `config/` und `scripts/` exakt auf dem getesteten Repository-Stand.

Nur wenn dieser Git-Stand nicht mehr verfügbar ist, die im Backup enthaltenen versionierten Kopien als Fallback verwenden:

```bash
cp <BACKUP_DIR>/configuration/compose.yml .
rm -rf config scripts
cp -a <BACKUP_DIR>/configuration/config .
cp -a <BACKUP_DIR>/configuration/scripts .
```

Diese Fallback-Kopien werden nicht an die neue Installation angepasst; sie repräsentieren den zum Backup gehörenden Stackstand.

## 13. Leere Zielvolumes erstellen

Nur bei einer bewusst neuen beziehungsweise leeren Zielinstallation vorhandene Part-DB-Volumes entfernen. **Vorher Namen und Backup mehrfach kontrollieren.**

```bash
for volume in \
  partdb_uploads \
  partdb_public_media \
  partdb_mariadb_data
do
  if docker volume inspect "$volume" >/dev/null 2>&1; then
    docker volume rm "$volume"
  fi
done
```

Danach werden die Volumes beim Start beziehungsweise explizit neu erzeugt.

```bash
docker volume create partdb_uploads
docker volume create partdb_public_media
docker volume create partdb_mariadb_data
```

Diesen Abschnitt bei einer In-place-Reparatur mit noch benötigten Volumes nicht blind ausführen.

## 14. MariaDB initialisieren

```bash
docker compose up -d mariadb
```

Warten:

```bash
watch -n 2 docker compose ps mariadb
```

Fortfahren, wenn MariaDB `healthy` ist.

Die leere Datenbank und der Datenbankbenutzer werden dabei aus `.env` und den ursprünglichen Secrets angelegt.

## 15. SQL-Dump einspielen

Auch beim Restore wird das Datenbankpasswort nicht als Prozessargument übergeben:

```bash
docker compose exec -T mariadb sh -c '
  CLIENT_CNF="$(mktemp)"
  trap "rm -f \"$CLIENT_CNF\"" EXIT HUP INT TERM
  chmod 600 "$CLIENT_CNF"

  {
    printf "[client]\nuser=%s\npassword=" "$MARIADB_USER"
    cat /run/secrets/mariadb_password
    printf "\n"
  } > "$CLIENT_CNF"

  mariadb \
    --defaults-extra-file="$CLIENT_CNF" \
    "$MARIADB_DATABASE"
' < <BACKUP_DIR>/databases/partdb.sql
```

Erwartet: keine Fehlermeldung. Die temporäre Client-Konfiguration wird nach dem Import automatisch entfernt.

## 16. Dateivolumes wiederherstellen

Part-DB ist noch nicht gestartet.

Uploads:

```bash
docker run --rm \
  -v partdb_uploads:/target \
  -v <BACKUP_DIR>/volumes:/backup:ro \
  alpine:3.24 \
  sh -c 'cd /target && tar -xzf /backup/partdb_uploads.tar.gz'
```

Öffentliche Medien:

```bash
docker run --rm \
  -v partdb_public_media:/target \
  -v <BACKUP_DIR>/volumes:/backup:ro \
  alpine:3.24 \
  sh -c 'cd /target && tar -xzf /backup/partdb_public_media.tar.gz'
```

## 17. Part-DB starten

```bash
docker compose up -d
docker compose ps
docker compose logs --tail=250 partdb
```

Weil `DB_AUTOMIGRATE=true` aktiv ist, würde ein neueres Part-DB-Image beim Start gegebenenfalls Migrationen durchführen. Deshalb für den ersten Restore-Test bewusst die zum Backup passende Version verwenden.

## 18. Funktion nach Restore prüfen

Mindestens:

```bash
curl -I http://partdb.<DOMAIN>
```

Zusätzlich im Browser:

- äußere Authentik-Weiterleitung,
- lokaler Notfalladministrator,
- SAML-Anmeldung,
- Gruppenzuordnung,
- Partliste und Anhänge,
- öffentliche Medien,
- anonyme Berechtigungen,
- Schreibtest mit einem berechtigten Benutzer.

## 19. Core-/Authentik-Restore

Wenn auch der Core-Stack verloren ging, zuerst dessen Wiederherstellung durchführen:

- [Core: Backup und Wiederherstellung](../core/backup-und-wiederherstellung.md)

Danach kontrollieren, dass `Part-DB Access`, `Part-DB SSO`, Gruppen, Property Mapping und Zertifikate vorhanden sind.

Das lokale Part-DB-SP-Zertifikat kann zwar erneut in Authentik importiert werden, ersetzt aber nicht die übrige Authentik-Konfiguration und Benutzerzuordnung.

## 20. Restore-Test dokumentieren

Ein Restore ist erst geprüft, wenn mindestens dokumentiert wurde:

```text
Backup-Zeitpunkt:
Restore-Zeitpunkt:
Git-Commit:
Part-DB-Version:
MariaDB-Version:
Datenbankimport erfolgreich:
Uploads erfolgreich:
Public Media erfolgreich:
Forward Auth erfolgreich:
SAML erfolgreich:
Gruppenmapping erfolgreich:
Prüfer:
```

## Offizielle Referenzen

- [Part-DB: Backup & Restore Data](https://docs.part-db.de/usage/backup_restore.html)
- [Part-DB: Docker-Installation](https://docs.part-db.de/installation/installation_docker.html)
- [MariaDB: mariadb-dump](https://mariadb.com/kb/en/mariadb-dump/)
