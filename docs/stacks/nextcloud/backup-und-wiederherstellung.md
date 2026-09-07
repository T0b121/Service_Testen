# Nextcloud-Stack: Backup und Wiederherstellung

Allgemeine Regeln: [Backup und Wiederherstellung](../../backup-und-wiederherstellung.md).

## Zu sichernde Daten

- lokale `.env` und alle Dateien unter `secrets/` verschlüsselt
- Authentik-PostgreSQL-Backup einschließlich Nextcloud-OIDC-Provider und
  Client-Secret
- PostgreSQL-Dump von `nextcloud-postgresql`
- `nextcloud_html`
- alle `nextcloud_onlyoffice_*`-Volumes
- `jellyfin_media` nach dessen eigener Medien-Strategie

`nextcloud_redis_data` ist Cache und kann neu erzeugt werden; eine Sicherung
schadet nicht, ist aber für die Wiederherstellung nicht erforderlich.

## Datenbank sichern

```bash
cd <PROJEKT_ROOT>/Compose/nextcloud
BACKUP_DIR=<SICHERES_BACKUPVERZEICHNIS>
umask 077
mkdir -p "$BACKUP_DIR"
docker compose exec -T nextcloud-postgresql \
  sh -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc' \
  > "$BACKUP_DIR/nextcloud.dump"
```

## Volumes sichern

Für eine konsistente Sicherung Nextcloud, Cron und ONLYOFFICE kurz stoppen:

```bash
docker compose stop nextcloud nextcloud-cron onlyoffice
```

Beispiel für das zentrale Nextcloud-Volume:

```bash
docker run --rm \
  -v nextcloud_html:/source:ro \
  -v "$BACKUP_DIR:/backup" \
  alpine:3.24 \
  tar -C /source -czf /backup/nextcloud_html.tar.gz .
```

Alle `nextcloud_onlyoffice_*`-Volumes analog sichern, danach starten:

```bash
docker compose start nextcloud nextcloud-cron onlyoffice
docker compose ps
```

## Wiederherstellungsreihenfolge

1. identischen Git-Stand, `.env` und Secrets bereitstellen;
2. auf einer leeren Zielinstallation die benötigten Volumes erzeugen;
3. ONLYOFFICE- und Nextcloud-Volumearchive zurückspielen;
4. PostgreSQL starten und den Datenbankdump einspielen;
5. Nextcloud, Cron und ONLYOFFICE starten;
6. Anmeldung, Healthchecks und eine Office-Testdatei prüfen.

Ohne die ursprünglichen Secrets und das Authentik-Backup ist kein
verlässlicher Restore möglich.
