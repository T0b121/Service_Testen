# Uptime-Kuma-Stack: Betrieb

## Status und Logs

```bash
cd <PROJEKT_ROOT>/Compose/uptime-kuma
docker compose ps
docker compose logs --since=24h uptime-kuma
```

## Monitore verwalten

Monitore, Wartungsfenster, Benachrichtigungen und öffentliche Statusseiten
werden in der Uptime-Kuma-Oberfläche verwaltet. Die Erstkonfiguration der
zehn internen Monitore erfolgte über Kumas authentifizierte Socket-API; diese
Schnittstelle wird bei späteren Kuma-Updates erneut getestet, weil sie keine
stabile Drittanbieter-API garantiert.

Die aktuelle Monitorliste steht vollständig in
[Erststart und Prüfung](erststart-und-pruefung.md#6-eingerichtete-monitore-prüfen).

Öffentliche Statusseiten erst aktivieren, wenn ihr Inhalt wirklich ohne
Authentik sichtbar sein darf. Die Uptime-Kuma-Verwaltungsoberfläche bleibt
immer hinter Authentik.

## Update

Vor einem Update zuerst [Backup und Wiederherstellung](backup-und-wiederherstellung.md)
durchführen und die Release Notes prüfen. Anschließend:

```bash
cd <PROJEKT_ROOT>/Compose/uptime-kuma
docker compose pull
docker compose config --quiet
docker compose up -d
docker compose ps
docker compose logs --tail=150 uptime-kuma
```

Danach Anmeldung, mindestens einen Monitor und eine Benachrichtigung testen.

## Neustart

```bash
docker compose restart uptime-kuma
docker compose ps
```

Der Neustart löscht keine Monitore oder Einstellungen.

## Vertrag für die spätere zentrale Einrichtungs-CLI

Die heute manuell ausgeführten Schritte werden später durch eine zentrale
Python-CLI ersetzt. Jeder Stack erhält dafür eine eigene, versionierte
Python-Provisionierungskomponente in seinem Compose-Verzeichnis, zum Beispiel
`Compose/<stack>/provision.py`. Diese Komponente enthält nur die
dienstspezifische Einrichtung; Auswahl, Env-Vorlagen, Secret-Eingaben,
Compose-Lebenszyklus und Benutzerverwaltung bleiben Verantwortung der
zentralen CLI.

Die zentrale CLI übergibt jeder Stack-Komponente mindestens diese benannten
Parameter:

```text
--project-root       absoluter Projektpfad
--stack-dir          absolutes Compose-Verzeichnis des Stacks
--env-file           erzeugte lokale .env-Datei
--domain             einmalig aufgelöste Basisdomain
--authentik-url      interne oder öffentliche Authentik-Basisadresse
--authentik-token-file
                     Datei mit dem API-Token für die deklarative Authentik-Konfiguration
--secrets-dir        lokales, ignoriertes Secret-Verzeichnis des Stacks
--dry-run            nur geplante Änderungen ausgeben
```

Stapel dürfen keine Passwörter als Kommandozeilenargument übernehmen. Geheime
Werte werden ausschließlich über eine von `--secrets-dir` referenzierte Datei
oder über eine verdeckte lokale Eingabe verarbeitet.

Die spätere Uptime-Kuma-Komponente erhält zusätzlich:

```text
--kuma-url           interne Kuma-Adresse, derzeit http://uptime-kuma:3001
--kuma-username      lokaler Kuma-Notfalladministrator
--kuma-password-file ignorierte Passwortdatei für den API-Login
--monitor-spec       deklarative Monitorbeschreibung des aufrufenden Stacks
```

`--monitor-spec` beschreibt mindestens Monitorname, Typ, interne Zieladresse,
Akzeptanzcodes, Header und Intervall. Die Komponente muss idempotent sein:
existierende gleichnamige Monitore werden aktualisiert, fehlende angelegt und
der anschließende Heartbeat wird geprüft. Die aktuelle Instanz verwendet noch
keine solche Python-Komponente; ihre Einrichtung erfolgte unmittelbar über
Kumas API und ist oben vollständig dokumentiert.
