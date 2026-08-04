# LiteLLM-Stack: Backup und Wiederherstellung

## Backup-Umfang

| Daten | Speicherort | Bewertung |
|---|---|---|
| Virtual Keys, Benutzer, Modelle und Verwaltungsdaten | Volume `litellm_postgresql_data` | erforderlich |
| Datenbankpasswort, Master-Key, Salt-Key, OIDC-Secret und Fallback-Passwort | lokale `.env` | erforderlich, verschlüsselt sichern |
| Authentik-Anwendung, OIDC-Provider und Gruppenbindung | Authentik-PostgreSQL-Backup des Core-Stacks | erforderlich |

Ohne den ursprünglichen `LITELLM_SALT_KEY` können verschlüsselte Werte aus der
LiteLLM-Datenbank nicht zuverlässig entschlüsselt werden.

## Datenbank und Konfiguration sichern

`BACKUP_DIR` wie in der projektweiten
[Backup-Strategie](../../backup-und-wiederherstellung.md#4-zeitstempel-und-arbeitsvariablen)
setzen. Der PostgreSQL-Dump kann konsistent im laufenden Betrieb erstellt
werden:

```bash
cd <PROJEKT_ROOT>/Compose/litellm
test -n "${BACKUP_DIR:-}" || { echo 'BACKUP_DIR ist nicht gesetzt' >&2; exit 1; }
umask 077
mkdir -p "$BACKUP_DIR/configuration" "$BACKUP_DIR/databases"

cp .env "$BACKUP_DIR/configuration/.env"
cp config.yaml "$BACKUP_DIR/configuration/config.yaml"

docker compose exec -T litellm-postgresql \
  sh -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc' \
  > "$BACKUP_DIR/databases/litellm.dump"

docker compose exec -T litellm-postgresql \
  pg_restore --list \
  < "$BACKUP_DIR/databases/litellm.dump" \
  >/dev/null
```

Erwartet sind ein nicht leerer Dump und Exit-Code `0` bei `pg_restore`. Das
Backup enthält sämtliche LiteLLM-Schlüssel und muss anschließend verschlüsselt
werden.

## Wiederherstellung

1. Core-Stack und die Authentik-Konfiguration wiederherstellen.
2. Lokale `.env` mit unveränderten Geheimnissen im Modus `600` bereitstellen.
3. Den zum Backup gehörenden Git-Stand einschließlich `config.yaml`
   bereitstellen.
4. Auf einer neuen Zielinstallation ein leeres PostgreSQL-Volume initialisieren
   und den Dump einspielen.
5. LiteLLM starten und mit einem bestehenden Virtual Key `/v1/models` testen.
6. OIDC-Anmeldung bei Authentik und Zugriff auf `/ui` prüfen.

Das folgende Beispiel verweigert den Restore, wenn das Zielvolume bereits
existiert. Ein vorhandenes produktives Volume niemals automatisch ersetzen:

```bash
cd <PROJEKT_ROOT>/Compose/litellm
test -n "${BACKUP_DIR:-}" || { echo 'BACKUP_DIR ist nicht gesetzt' >&2; exit 1; }
docker compose down
if docker volume inspect litellm_postgresql_data >/dev/null 2>&1; then
  echo 'Volume litellm_postgresql_data existiert bereits; Restore-Ziel zuerst bewusst klären.' >&2
  exit 1
fi

docker compose up -d litellm-postgresql
docker compose ps litellm-postgresql
```

Erst fortfahren, wenn `litellm-postgresql` in der Statusausgabe `healthy`
erreicht hat:

```bash
docker compose exec -T litellm-postgresql \
  sh -c 'pg_restore --exit-on-error --clean --if-exists --no-owner --no-privileges -U "$POSTGRES_USER" -d "$POSTGRES_DB"' \
  < "$BACKUP_DIR/databases/litellm.dump"

docker compose up -d
docker compose ps
```
