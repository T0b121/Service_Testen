# Backup und Wiederherstellung

Dieses Dokument beschreibt die stackübergreifende Strategie. Konkrete Daten und Befehle stehen zusätzlich in der jeweiligen Stack-Dokumentation.

## 1. Ziele

Ein Backup ist erst vollständig, wenn:

- alle benötigten Daten enthalten sind,
- Secrets und Konfiguration enthalten sind,
- die Sicherung verschlüsselt aufbewahrt wird,
- Prüfsummen kontrolliert werden,
- die Wiederherstellung dokumentiert ist,
- ein Restore-Test erfolgreich durchgeführt wurde.

## 2. Backup-Inventar

Für jeden Stack werden mindestens geprüft:

- `compose.yml`
- `.env`
- `secrets/`
- Datenbankdumps
- persistente Volumes
- Zertifikats- und ACME-Daten
- externe Abhängigkeiten
- verwendete Image-Tags
- Wiederherstellungsreihenfolge

Nicht jedes Volume wird gleich gesichert. Datenbanken werden bevorzugt über anwendungskonsistente Dumps gesichert.

## 3. Ablagestruktur

Beispiel:

```text
backups/
└── 2026-07-26T190000Z/
    ├── manifest.txt
    ├── checksums.sha256
    ├── configuration/
    ├── secrets/
    ├── databases/
    └── volumes/
```

Backup-Verzeichnisse gehören nicht in Git.

Empfohlene `.gitignore`-Einträge:

```gitignore
backups/
**/backups/
*.dump
*.backup
```

## 4. Zeitstempel

```bash
BACKUP_TIMESTAMP="$(date -u +%Y-%m-%dT%H%M%SZ)"
mkdir -p "backups/$BACKUP_TIMESTAMP"
```

UTC-Zeitstempel vermeiden Mehrdeutigkeiten bei Sommerzeit und Zeitzonen.

## 5. Prüfsummen

Erstellen:

```bash
find "backups/$BACKUP_TIMESTAMP" \
  -type f \
  ! -name checksums.sha256 \
  -print0 \
  | sort -z \
  | xargs -0 sha256sum \
  > "backups/$BACKUP_TIMESTAMP/checksums.sha256"
```

Prüfen:

```bash
cd "backups/$BACKUP_TIMESTAMP"
sha256sum -c checksums.sha256
```

SHA-256 weist Dateiänderungen nach. Es verschlüsselt das Backup nicht und beweist ohne zusätzliche Signatur nicht, wer die Prüfsumme erstellt hat.

## 6. Backup-Verschlüsselung

Backups enthalten Passwörter, Schlüssel, Benutzerdaten und Zertifikate. Sie müssen verschlüsselt gespeichert und übertragen werden.

Wenn ein Backup-Programm eine zufällige Passphrase benötigt:

```bash
umask 077
openssl rand -base64 32 \
  | tr -d '\n' \
  > backup-encryption-password
```

Regeln:

- Schlüssel oder Passphrase nicht im gleichen Speicherort wie das Backup ablegen.
- Kopie in einem Passwortmanager oder getrennten sicheren Tresor speichern.
- Dateimodus `600` setzen.
- Keine Passphrase als Shellargument übergeben, wenn sie dadurch in Prozesslisten oder Shell-History sichtbar wird.
- Base64 ist keine Verschlüsselung.

Geeignete Werkzeuge sind beispielsweise Restic, BorgBackup, age oder GnuPG. Die konkrete Auswahl hängt vom Backupziel ab.

## 7. Aufbewahrung

Mindestens:

- mehrere Generationen,
- mindestens eine Kopie außerhalb des Servers,
- mindestens eine gegen versehentliches Löschen geschützte Kopie,
- dokumentierte Löschfristen,
- regelmäßige Überprüfung des freien Speicherplatzes.

Ein mögliches Schema:

```text
7 tägliche
4 wöchentliche
12 monatliche
```

Das Schema ist an Änderungsrate, Speichervolumen und Wiederanlaufziel anzupassen.

## 8. Datenbankdumps

Datenbanken werden im laufenden Betrieb nicht durch blindes Kopieren ihres Volume-Dateisystems gesichert.

Stattdessen:

- PostgreSQL: `pg_dump` beziehungsweise `pg_dumpall`
- MySQL/MariaDB: anwendungskonsistentes Dumpwerkzeug
- andere Datenbanken: herstellerspezifisches Backupverfahren

Ein Dump muss nach Erstellung mindestens lesbar geprüft werden.

Für PostgreSQL-Custom-Dumps:

```bash
pg_restore --list DATEI.dump >/dev/null
```

## 9. Volume-Sicherungen

Vor einer dateibasierten Volume-Sicherung prüfen:

- schreibt die Anwendung während des Backups?
- kann der Dienst kurz gestoppt werden?
- gibt es ein anwendungseigenes Exportverfahren?
- bestehen Abhängigkeiten zu einer Datenbank?
- müssen Dateibesitzer und Berechtigungen erhalten bleiben?

Bei kritischen Daten wird der schreibende Dienst vorübergehend gestoppt oder ein konsistenter Snapshot verwendet.

## 10. Manifest

Jedes Backup erhält ein Manifest, beispielsweise:

```text
Backup-Zeitpunkt:
Hostname:
Betriebssystem:
Docker-Version:
Compose-Version:
Stack:
Image-Tags:
Enthaltene Daten:
Nicht enthaltene Daten:
Verschlüsselungsverfahren:
Prüfsumme:
Besondere Wiederherstellungshinweise:
```

Versionsinformationen:

```bash
{
  date -u
  hostnamectl
  docker --version
  docker compose version
  docker compose config --images
} > manifest.txt
```

## 11. Restore-Test

Ein Restore-Test sollte:

1. auf einem isolierten Testsystem erfolgen,
2. mit Kopien der Produktiv-Backups arbeiten,
3. DNS und öffentliche Ports nicht versehentlich übernehmen,
4. Secrets und Daten wiederherstellen,
5. Healthchecks prüfen,
6. Benutzeranmeldung testen,
7. das Ergebnis dokumentieren.

Nur das Erstellen einer Archivdatei ist kein Restore-Test.

## 12. Verlust einzelner Komponenten

### `.env` verloren

Werte müssen aus Dokumentation und Backup rekonstruiert werden. Falsche Volume-Namen können wie leere Neuinstallationen wirken.

### Secret verloren

Ein Secret darf nicht blind neu generiert werden. Es kann mit bestehenden Daten verknüpft sein.

### ACME-Daten verloren

Zertifikate können neu ausgestellt werden, aber Rate-Limits und temporäre Ausfälle sind möglich.

### Datenbankdump beschädigt

Prüfsummen und mehrere Backupgenerationen verwenden.

## 13. Stack-spezifische Dokumente

- [Core: Backup und Wiederherstellung](stacks/core/backup-und-wiederherstellung.md)
