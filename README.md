# Compose Stack Manager

Ein Python-Terminalprogramm verwaltet die 19 Stacks in `compose/`: Konfiguration,
Secrets, Abhängigkeiten, Docker-Ressourcen, Authentik, Nutzer und Mount-Backups.

**Status: Implementierung mit automatisierten Tests und Compose-Konfigurationsprüfung.
Ein vollständiger Live-Test mit Docker, Authentik und den Anwendungen steht noch aus.**
Vor produktiver Nutzung zuerst auf einer frischen Testinstallation prüfen.

## Einstieg

Siehe [SCHNELLSTART.md](SCHNELLSTART.md). Ohne Argumente startet
`compose/manage.py` das Terminalmenü. `core` ist immer ausgewählt; notwendige
Abhängigkeiten werden automatisch ergänzt. Bestehende Daten werden beim Abwählen
oder Stoppen eines Stacks nicht entfernt.

| Menüpunkt | Funktion |
|---|---|
| Ersteinrichtung | Stacks wählen, Werte erfassen, Core und Anwendungen einrichten |
| Start / Stop / Neustart | Aktivierte Stacks in Abhängigkeitsreihenfolge verwalten |
| Konfiguration bearbeiten | Echte `.env` bearbeiten, prüfen und Container neu erstellen |
| Stack-Auswahl ändern | Auswahl ändern und vorhandene Konfiguration weiterverwenden |
| Nutzerverwaltung | Authentik-Benutzer und Dienstgruppen verwalten |
| Backups / Import / Export | Mounts sichern, wiederherstellen und Zeitpläne verwalten |
| Status | Gewählte Stacks, erledigte Schritte und ausstehende Aktionen |

Die bestehende Installation und Dokumentation liegen unverändert in `_alt/`.
Neue Volumes tragen das Präfix `managed_`; alte Volumes werden nicht automatisch
übernommen. Container- und Netzwerknamen können sich mit einer alten laufenden
Installation überschneiden. Alte Stacks vor einer neuen Installation geordnet
stoppen; **keine Volumes löschen**.

## Erweiterung

Ein neuer Ordner `compose/<name>/` enthält:

- `compose.yml`: Dienste und Ressourcen einschließlich Secret-Dateizuordnung.
- `.env.example`: feste Werte und Referenzen für Eingaben.
- `stack.py`: Abhängigkeiten, Authentik-Gruppen, Router, SSO und besondere Aktionen.

Ordner mit führendem `_` werden übersprungen. Es gibt keine zentrale Stack-Liste.
Stack-Module sind vertrauenswürdiger Python-Code und werden lokal importiert.
Ein Beispiel und die Schnittstellen stehen in [docs/manager.md](docs/manager.md).

## Zugriff und Konfiguration

Alle externen HTTP-Anwendungsrouten haben Forward Auth. Nur Authentiks Login und
explizite Outpost-Rückwege bleiben frei erreichbar. Interne Containerverbindungen
bleiben direkt. SSO ergänzt Forward Auth; es ersetzt es nicht. Externe APIs,
Webhooks, Git-Clients und Office-Integrationen müssen deshalb auch die äußere
Authentifizierung bewältigen. Es werden keine stillen API-Ausnahmen angelegt.

Die CLI legt Gruppen ohne Mitglieder an. Der initiale Authentik-Administrator
`akadmin` wird einmal angezeigt und anschließend aus der Bootstrap-Datei entfernt.
Der Verwaltungs-API-Token bleibt als geschütztes Core-Secret erhalten.

Passworteingaben bleiben unsichtbar. `generate=` zeigt einen Befehl an, führt ihn
aber nicht aus. `@file:/absoluter/pfad` liest Schlüssel und mehrzeilige Zertifikate.
Normale `.env`-Dateien und Verwaltungszustand haben Modus `600`. Compose-Dateisecrets
nutzen `640` und die ausschließlich für Container eingerichtete Gruppe
`stack-manager-secrets` (GID `60001`); Secret-Verzeichnisse haben `750`. Dies macht
Dateisecrets auch für Non-root-Images lesbar. Es werden keine Host-Nutzer zur Gruppe
hinzugefügt. Ein bereits anderweitig belegter GID wird als Fehler gemeldet.

Der Editor zeigt die tatsächlichen ENV-Werte. Gemeinsame normale Referenzen werden
in vorhandenen Stack-Konfigurationen gemeinsam geändert. Eine Passwortrotation in
einer bestehenden Datenbank ist eine eigene Betriebsaufgabe; der Editor verhindert
reine Dateiänderungen an vertraulichen Eingaben.

## Backups

Auswahl: Stack → Service → Volumes/Bind-Mounts. Auch einzelne Dateien sind möglich.
Sockets und Geräte werden ausgeschlossen. Alle laufenden Container mit denselben
oder überlappenden Mounts werden für die Sicherung gestoppt und danach gestartet.
Die Erkennung berücksichtigt auch Container außerhalb des gewählten Stacks.

Archive liegen standardmäßig unter `compose/_backup/<stack>/<service>/` und enthalten
ein Manifest. Vor dem Import werden Pfade und Links geprüft; Ziele müssen explizit
gewählt und das Ersetzen bestätigt werden. Absolute und aus dem Mount herausführende
Links sowie privilegierte setuid/setgid-Einträge werden abgewiesen. ACLs und erweiterte
Dateiattribute sind nicht Bestandteil dieses Formats.

ENV und Secrets können zusätzlich mit `age` verschlüsselt gesichert werden. Den
privaten age-Schlüssel außerhalb dieses Servers aufbewahren. Datenarchive ohne
Konfiguration können ebenfalls sensible Anwendungsdaten enthalten.

Zeitpläne verwenden fünfteilige Cron-Ausdrücke und eine IANA-Zeitzone. Der über das
Backup-Menü installierbare systemd-Timer prüft jede Minute. Ohne installierten Timer
läuft kein unbeaufsichtigter Auftrag. Alte Archive eines Auftrags werden erst nach
einer erfolgreichen neuen Sicherung entfernt. Ein verpasster Termin wird beim
nächsten Aufruf einmal nachgeholt. Fehler sind im Status sichtbar.

## Prüfungen

```bash
python -m unittest discover -s tests -v
python compose/manage.py check
python tests/validate_compose.py
```

Die letzte Prüfung benötigt das Docker-Compose-Plugin, aber keinen laufenden
Docker-Daemon. Sie verwendet ausschließlich temporäre Testwerte und startet nichts.
Details und noch erforderliche Betriebsprüfungen: [docs/validierung.md](docs/validierung.md).

## Interaktive Code-Analyse

Die [Graphify-Analyse auf GitHub Pages](https://t0b121.github.io/Service_Testen/)
zeigt Code-Verbindungen, Aufrufbeziehungen, einen Dateibaum und ein Stack-Inventar.
Der analysierte Commit und die Grenzen stehen auf der Startseite.

Ein committeter HTML-Snapshot liegt unter [`docs/graphify/`](docs/graphify/).
[Build-Anleitung und Umfang](tools/graphify/README.md); offene Arbeiten: [Issue #1](https://github.com/T0b121/Service_Testen/issues/1).
