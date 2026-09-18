# Paperless-ngx: Übersicht

Paperless-ngx archiviert eingehende Dokumente lokal, erzeugt durchsuchbare
PDF/A-Dateien und verwaltet Metadaten, Volltext sowie Berechtigungen.

| Komponente | Funktion | Öffentlich |
|---|---|---|
| Paperless | Weboberfläche, OCR, API und Consumer | `https://paperless.<DOMAIN>` |
| PostgreSQL | Metadaten | Nein |
| Valkey | Aufgabenwarteschlange | Nein |

Dokumente liegen im Docker-Volume `paperless_media`; Datenbank, Suchindex und
Klassifikationsdaten in separaten Volumes. RustFS/S3 ist ausdrücklich kein
aktiver Dokumentenspeicher, sondern späteres Ziel für Backups und Exporte.

Die Browser-Anmeldung erfolgt nativ über Authentik OIDC. `paperless-users`
steuert den Zugang und `paperless-admins` wird beim OIDC-Login auf die
Paperless-Administratorrolle abgebildet. Der lokale Admin ist ausschließlich
ein Notfallzugang.

Andere Dienste erhalten keinen Dateisystem-, Datenbank- oder S3-Zugriff.
Automationen verwenden später dedizierte Paperless-API-Token mit minimalen
Berechtigungen.
