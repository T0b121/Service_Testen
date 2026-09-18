# RustFS-Stack: Backup und Wiederherstellung

RustFS speichert Buckets, Objektinhalte, Benutzer und Policies dauerhaft im
Volume `rustfs_data`. Ein vollständiges Backup enthält zusätzlich die lokale
`.env` und alle Dateien unter `secrets/`; diese Konfigurationsdaten liegen
nicht im Docker-Volume.

## Sicherung

1. Ein verschlüsseltes Backupverzeichnis außerhalb des Repositorys vorbereiten
   (siehe [globale Backup-Anleitung](../../backup-und-wiederherstellung.md)).
2. Stack geordnet stoppen, damit keine Objekt- oder Metadatenänderung während
   der Dateisicherung erfolgt:

```bash
cd <PROJEKT_ROOT>/Compose/rustfs
docker compose stop rustfs
```

3. Volume in ein Backupverzeichnis archivieren und Konfiguration sowie Secrets
   verschlüsselt, aber getrennt sichern. Besitzer und Modi müssen erhalten
   bleiben.
4. Stack wieder starten und beide internen Healthchecks ausführen.

Das Volume nicht mit `docker compose down -v` löschen. Dieser Befehl würde
den gesamten S3-Bestand entfernen.

## Wiederherstellung

1. RustFS stoppen.
2. Eine defekte oder leere Instanz erst nach Sicherung des Ist-Zustands
   ersetzen.
3. `rustfs_data` aus dem getesteten Backup wiederherstellen.
4. Die zugehörige `.env` und alle Secret-Dateien mit ihren ursprünglichen
   Werten und restriktiven Rechten wiederherstellen.
5. Stack starten.
6. Interne Healthchecks, Forward Auth, OIDC-Anmeldung und einen Lese-/Schreib-
   Test eines berechtigten Service-Accounts durchführen.

Der Verlust des Root-Secret oder des OIDC-Client-Secrets darf nicht durch
blindes Neugenerieren ersetzt werden: Beide können bestehende Zugriffe oder
die native Anmeldung unbrauchbar machen.
