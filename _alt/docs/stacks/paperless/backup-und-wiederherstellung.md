# Paperless-ngx: Backup und Wiederherstellung

Der aktive Dokumentbestand liegt absichtlich lokal in den Docker-Volumes
`paperless_media`, `paperless_data`, `paperless_consume`, `paperless_export`
und `paperless_postgresql_data`. RustFS wird nicht als aktiver Speicher
verwendet.

Ein vollständiges Backup enthält mindestens:

- den PostgreSQL-Dump,
- die Volumes `paperless_media` und `paperless_data`,
- die lokalen Paperless-Secrets einschließlich des Session-Keys,
- bei Bedarf `paperless_export` und `paperless_consume`.

RustFS ist ein geeigneter, separater Zielort für verschlüsselte Backups oder
Exports. Ein automatischer Backup-Job wird erst eingerichtet, wenn das
Aufbewahrungsziel und der Sicherungsrhythmus festgelegt sind; ein ungetesteter
S3-Job ersetzt kein prüfbares Backup.
