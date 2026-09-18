# Paperless-ngx: Erststart und Prüfung

Zuerst den Stack starten:

```bash
cd <PROJEKT_ROOT>/Compose/paperless
docker compose pull
docker compose up -d
docker compose ps
```

Danach richtet das Skript den separaten OIDC-Client, die Authentik-Anwendung,
beide Authentik-Gruppen sowie die passenden lokalen Paperless-Gruppen ein:

```bash
./scripts/configure-authentik-oidc.sh
docker compose up -d --force-recreate paperless
```

Prüfpunkte:

1. `https://paperless.<DOMAIN>` öffnet die Anmeldung.
2. **Authentik** leitet zurück zu Paperless.
3. Ein Mitglied von `paperless-users` kann sich anmelden.
4. Ein Mitglied von `paperless-admins` hat Paperless-Administrationsrechte.
5. Ein Test-PDF wird hochgeladen, OCR-verarbeitet und über die Suche gefunden.
6. `docker compose ps` zeigt Paperless, PostgreSQL und Valkey gesund an.

Der anfänglich erzeugte lokale Admin wird erst nach erfolgreichem OIDC-Test im
Passwortmanager als Notfallzugang verwahrt; sein Passwort wird nicht gelöscht.
