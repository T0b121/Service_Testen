# Umsetzung des Stack-Managers

Branch: `codex/stack-manager`, Ausgangspunkt: `4c45727`.
Jede nummerierte Aufgabe wird separat committet; die Übertragung erfolgt zusätzlich pro Stack.

1. Vorhandene Compose-Dateien und Dokumentation unverändert nach `_alt` verschieben.
2. Stack-Vertrag, Erkennung, Abhängigkeiten, Zustand und Sperre.
3. ENV-Parser, Referenzen, vertrauliche Eingabe und Secret-Dateien.
4. Docker-Compose-Ausführung, Ressourcen, Bereitschaft und Lebenszyklus.
5. Authentik-API, Bootstrap, Gruppen, Forward Auth und Icons.
6. Alle 19 Stacks jeweils mit eigenem Commit übertragen.
7. Native SSO-Konfiguration und besondere Stack-Aktionen.
8. Benutzer und Dienstgruppen verwalten, ausstehende Aktionen anzeigen.
9. Mount-Inventar, konsistenter Export und geprüfter Import.
10. Cron-Zeitpläne, Zeitzone, Dienst und Aufbewahrung.
11. Interaktives Terminalmenü, Checkboxen und ENV-Editor.
12. Dokumentation und abschließende Integrationstests.

## Verbindliche Grenzen

- Keine Übernahme alter Volumes, kein Löschen des bisherigen Bestands.
- `.gitignore` nur ergänzen. Lokale Daten, Secrets und Backups nicht versionieren.
- `core` immer aktiv. Neue Stacks werden durch drei Dateien entdeckt.
- Gemeinsame Aufgaben ausschließlich im Manager; `stack.py` beschreibt Besonderheiten.
- Externe HTTP-Anwendungsrouten immer mit Forward Auth; Authentik-Anmeldung und
  notwendige Outpost-Rückwege bleiben erreichbar. Interne Verbindungen bleiben direkt.
- Gruppen zunächst ohne Nutzer. SSO zusätzlich, sofern die Anwendung es unterstützt.
- Passworteingaben verdeckt; Erzeugungsbefehle nur anzeigen.
- Backups von ausgewählten Volumes und Bind-Mounts unter `_backup/<stack>/<service>`.
- Kein Erfolgsstatus für fehlgeschlagene oder nur teilweise ausgeführte Einrichtung.

## Validierung

Automatisierte Tests für Parser, Referenzen, Abhängigkeiten, Auth-Plan,
Archivvalidierung und Scheduler; statische Prüfung aller Stack-Vorlagen.
Eine laufende Docker-Engine und Authentik-Instanz sind in der Entwicklungsumgebung nicht
vorhanden. Die Konfiguration wurde zusätzlich mit dem offiziellen Compose-Parser geprüft. Echte Containerstarts, SSO-Logins und Wiederherstellungen auf Docker
werden daher ausdrücklich als ausstehende Betriebsprüfung dokumentiert.

## Implementierungsstand

Die Aufgaben wurden in einzelnen Commits umgesetzt. Die 19 Stacks haben jeweils
einen eigenen Übertragungscommit; danach folgen getrennte Integrationskorrekturen.
Die noch notwendigen Live-Prüfungen sind in `validierung.md` aufgeführt.
