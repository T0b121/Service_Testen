# Validierung

In der Entwicklungsumgebung erfolgreich ausgeführt:

- Python-Tests für Abhängigkeiten und Kreisfehler, gemeinsame Eingaben und Wiederholung,
  ENV-Sonderzeichen/JSON, verpflichtendes Forward Auth, Cron-Zeitzonen,
  Archiv-Pfadvalidierung und den Export-/Import-Rundlauf.
- Stack-Vertragsprüfung für alle 19 Ordner.
- `docker compose config --format json` für alle 19 Stacks mit ausschließlich
  temporären Testwerten, Docker Compose v2.39.4. Keine Images heruntergeladen oder gestartet.
- Archivierungsprüfung: alle ursprünglich versionierten Dateien außer `.gitignore`
  sind unter `_alt/` bytegleich vorhanden; die ursprüngliche `.gitignore` bleibt als
  unveränderter Anfang der ergänzten Datei erhalten.

Noch auf einem Test-Docker-Host erforderlich:

1. Core-Ersteinrichtung, einmalige Adminanzeige und Wiederholung nach Abbruch.
2. Jeden Stack starten; Healthchecks und besondere Einrichtungsaktionen prüfen.
3. Mit einem Testnutzer ohne Gruppe, mit Dienstgruppe und nach Entzug anmelden.
   Forward Auth und den zusätzlichen OIDC-/SAML-Login jeweils separat testen.
4. Part-DB-Gruppenmapping/anonyme Rechte, Nextcloud-Adminmapping, Paperless-Gruppen
   und GitLab-Kontosperre prüfen. Benutzeradapter sind versionsabhängige Integration.
5. Export eines Test-Volumes und Bind-Mounts, gezielte Änderung und Wiederherstellung.
   Besitzer, Rechte und relative Links kontrollieren. Verschlüsseltes Konfigurationsarchiv
   mit separat verwahrter age-Identität wiederherstellen.
6. Timer bei geschlossener CLI, Fehlerfall, Aufbewahrung und gemeinsame Mount-Nutzer prüfen.

Das Repository behauptet keinen erfolgreichen Live-Test dieser Schritte. Insbesondere
bleiben reale IdP-Callbacks, versionsabhängige Anwendungskommandos und das Zusammenspiel
von externen API-Clients mit verpflichtendem Forward Auth vor Ort zu prüfen.

Referenzen für die Implementierung:

- [Authentik Bootstrap](https://docs.goauthentik.io/install-config/automated-install/)
- [Authentik 2026.5 Datei-API](https://github.com/goauthentik/authentik/blob/version/2026.5.0/authentik/admin/files/api.py)
- [Nextcloud OIDC Provider-Kommando](https://github.com/nextcloud/user_oidc/blob/main/lib/Command/UpsertProvider.php)
- [Part-DB Benutzerrechte-Kommando](https://github.com/Part-DB/Part-DB-server/blob/master/src/Command/User/UsersPermissionsCommand.php)
