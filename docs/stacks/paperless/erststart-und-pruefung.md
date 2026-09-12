# Paperless-ngx: Erststart und Prüfung

Nach der OIDC-Konfiguration starten:

```bash
cd <PROJEKT_ROOT>/Compose/paperless
docker compose pull
docker compose up -d
docker compose ps
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
