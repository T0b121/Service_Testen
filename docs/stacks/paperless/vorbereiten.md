# Paperless-ngx: Vorbereiten

```bash
cd <PROJEKT_ROOT>/Compose/paperless
cp .env.example .env
chmod 600 .env
./scripts/bootstrap-secrets.sh
docker compose config --quiet
```

Das Skript erzeugt lokale Secrets für PostgreSQL, den Paperless-Session-Key
und den einmaligen lokalen Notfalladministrator. Diese Dateien gehören in den
Passwortmanager, nie in Git oder in Chat-Ausgaben.

Paperless speichert Originale und archivierte Dokumente im lokalen Volume
`paperless_media`. Für Standard-PDFs und Scans sind keine zusätzlichen
Konverter nötig. Office-Dateien und E-Mails mit Anhängen können später bei
Bedarf mit Tika und Gotenberg ergänzt werden.

Weiter mit [Erststart und Prüfung](erststart-und-pruefung.md).
