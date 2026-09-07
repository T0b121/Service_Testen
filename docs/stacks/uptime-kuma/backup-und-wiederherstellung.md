# Uptime-Kuma-Stack: Backup und Wiederherstellung

## Backup-Inventar

| Bestandteil | Sichern | Begründung |
|---|---|---|
| Volume `uptime_kuma_data` | Ja | enthält Datenbank, Benutzer, Monitore, Benachrichtigungen und Einstellungen |
| `Compose/uptime-kuma/compose.yml` | über Git | reproduzierbare Stackdefinition |
| `.env` | verschlüsselt | Basisdomain und Versionslinie |
| `secrets/uptime_kuma_admin_password` | verschlüsselt | lokaler Kuma-Notfallzugang |

## Backup erstellen

Der Stack kann während eines konsistenten Dateibackups kurz angehalten werden:

```bash
cd <PROJEKT_ROOT>/Compose/uptime-kuma
docker compose stop uptime-kuma
docker run --rm \
  -v uptime_kuma_data:/source:ro \
  -v "$PWD":/backup \
  alpine:3.22 \
  tar -C /source -czf /backup/uptime-kuma-data-$(date +%F).tar.gz .
docker compose start uptime-kuma
```

Das erzeugte Archiv enthält die Embedded-MariaDB und alle Kuma-Daten und muss
verschlüsselt gesichert werden. Die Secret-Datei des lokalen
Notfalladministrators separat verschlüsselt sichern. Nach dem Backup den Stack
prüfen:

```bash
docker compose ps
```

## Wiederherstellung

1. Stack anhalten.
2. Das bestehende Volume nur nach einem zusätzlichen Sicherheitsbackup
   ersetzen.
3. Ein leeres Volume `uptime_kuma_data` anlegen.
4. Archiv in das neue Volume entpacken.
5. Stack starten und Anmeldung sowie Monitore prüfen.

Beispiel für Schritt 4, nachdem ein leeres Volume bereitsteht:

```bash
docker run --rm \
  -v uptime_kuma_data:/target \
  -v "$PWD":/backup:ro \
  alpine:3.22 \
  sh -ec 'tar -C /target -xzf /backup/UPTIME_KUMA_BACKUP.tar.gz'
```

`UPTIME_KUMA_BACKUP.tar.gz` durch den tatsächlichen Archivnamen ersetzen.
Die Wiederherstellung zuerst mit einer Kopie des Backups testen.
