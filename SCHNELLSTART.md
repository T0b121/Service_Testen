# Schnellstart

Voraussetzungen: lokaler Linux-Docker-Host, Docker Engine mit Compose-Plugin,
Python ab 3.12, `python3-venv`, `openssl`, systemd für Zeitpläne; `age` für verschlüsselte
Konfigurationsbackups. DNS der gewählten Subdomains muss auf den Server zeigen,
Port 80/443 muss für Traefik erreichbar sein. Die CLI verwendet root für
Mount-Zugriff und Secret-Dateirechte.

## 1. Python-Umgebung vorbereiten

Im Repository:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python compose/manage.py check
```

Die normale Prüfung benötigt kein Docker und verändert keine Container.

## 2. Menü öffnen

```bash
sudo .venv/bin/python compose/manage.py
```

**Ersteinrichtung** wählen. Mit Leertaste Stacks auswählen, mit Tab zu OK wechseln.
`core` ist immer aktiv. Anschließend Werte eingeben. Passwörter sind nicht sichtbar;
angezeigte Erzeugungsbefehle werden separat ausgeführt. Zertifikate mit
`@file:/absoluter/pfad` einlesen. Bei vorhandenen Konfigurationen werden Werte wiederverwendet.

Der Manager startet Core und zeigt den Authentik-Erstzugang einmalig an. Im
Passwortmanager speichern und bestätigen. Bei einem Fehler die Ursache prüfen
und Ersteinrichtung erneut ausführen; vorhandene Werte bleiben erhalten.

## 3. Nutzer und Betrieb

Über **Nutzerverwaltung** Benutzer anlegen und Dienstgruppen zuweisen. Ein neues
Konto erhält zunächst keine Dienstberechtigung. **Status** zeigt ausstehende
anwendungsspezifische Synchronisierungen und Icon-Fehler.

Für Backups im Menü einen Zeitplan erstellen und anschließend **Automatische
Ausführung installieren** wählen. Das installiert `stack-manager-backup.timer`.
Der Timer verwendet denselben Python-Pfad; Repository und `.venv` danach nicht
verschieben, ohne den Timer erneut zu installieren.

CLI-Befehle ohne Menü:

```bash
sudo .venv/bin/python compose/manage.py setup --stacks partdb
sudo .venv/bin/python compose/manage.py start
sudo .venv/bin/python compose/manage.py stop
sudo .venv/bin/python compose/manage.py backup-tick
```

Die [kompakten Diensteseiten](docs/dienste.md) erklären die einzelnen Anwendungen.

Vor produktiver Nutzung die [Betriebsprüfungen](docs/validierung.md) durchführen.
