# Uptime Kuma

[Alle Dienste](../dienste.md) · [Schnellstart](../../SCHNELLSTART.md)

## Was macht der Dienst?

Uptime Kuma überwacht die Erreichbarkeit von Diensten.
Monitore prüfen beispielsweise HTTP-Endpunkte und zeigen Ausfälle an.
Benachrichtigungen müssen passend zum gewünschten Kanal eingerichtet werden.
Der Stack hält seinen Anwendungszustand in einem persistenten Volume.
Ein grüner Monitor sagt nur aus, dass seine konkrete Prüfung erfolgreich war.

## Einordnung in diesem Repository

| Punkt | Konfiguration |
|---|---|
| Stack-ID | `uptime-kuma` |
| Browseradresse | `https://uptime.<DOMAIN>` |
| Direkte Abhängigkeiten | [core](core.md) |
| Anmeldung | Forward Auth; kein nativer SSO-Adapter in diesem Stack. |
| Deklarierte Dienstgruppen | `uptime-kuma-admins`, `uptime-kuma-users` |

`<DOMAIN>` steht für die bei der Einrichtung gewählte Basisdomain.
Abhängigkeiten werden vom Manager ergänzt; weitere indirekte Stacks können dazukommen.
Eine Dienstgruppe regelt den äußeren Zugang, nicht automatisch jede Berechtigung innerhalb der Anwendung.

## Bestandteile

| Compose-Service | Container-Image |
|---|---|
| `uptime-kuma` | `louislam/uptime-kuma:${UPTIME_KUMA_VERSION}` |

Image-Variablen werden aus der Stack-Konfiguration aufgelöst.
Die Tabelle beschreibt den Repository-Stand, keine Liste bereits gestarteter Container.

## Einrichten und starten

Den [Schnellstart](../../SCHNELLSTART.md) einmal für den Host durchführen.
Danach im Manager **Ersteinrichtung** beziehungsweise **Stack-Auswahl ändern** öffnen:

```bash
sudo .venv/bin/python compose/manage.py
```

`uptime-kuma` auswählen und die ermittelten Abhängigkeiten kontrollieren.
Vorhandene Werte werden wiederverwendet; neue Secrets gehören nicht in Git.
Erst nach erfolgreicher Einrichtung mit der Nutzung beginnen.

## Erste Nutzung

1. Die Oberfläche unter `uptime.<DOMAIN>` öffnen und den Anwendungserstzugang einrichten.
2. Einen Monitor für einen einfachen, eindeutig erreichbaren Testdienst anlegen.
3. Intervall und erwartete Antwort bewusst wählen.
4. Einen kontrollierten Ausfall simulieren und die Statusänderung beobachten.
5. Erst danach den Benachrichtigungskanal aktivieren und dessen Zustellung testen.

## Wichtige Einstellungen

| Einstellung | Bedeutung |
|---|---|
| `UPTIME_KUMA_VERSION` | Version der Überwachungsanwendung. |
| `DOMAIN` | Basis für `uptime.<DOMAIN>`. |

Die vollständigen Eingaben stehen in [`.env.example`](../../compose/uptime-kuma/.env.example).
Normale Werte im Manager über **Konfiguration bearbeiten** ändern.
Passwortwechsel sind keine bloßen Textänderungen: Datei und laufender Dienst müssen zusammenpassen.

## Besonderheiten dieser Konfiguration

- Die Konfiguration aktiviert die eingebettete MariaDB der eingesetzten Kuma-Version.
- Es gibt hier keinen nativen SSO-Hook; die äußere Anmeldung allein verwaltet keine Kuma-Konten.
- Der Container befindet sich im Netz `web` und kann dort erreichbare Dienste intern prüfen.
- Ein öffentlicher geschützter Endpoint kann eine Loginseite liefern, obwohl die Anwendung dahinter defekt ist.
- Ein interner Monitor prüft wiederum nicht automatisch DNS, Zertifikat und externen Proxyweg.
- Für kritische Dienste beide Sichtweisen bewusst unterscheiden; nicht jeden 200-Status als vollständigen Funktionstest behandeln.

## Daten und Sicherung

| Volume-Schlüssel | Tatsächlicher Volume-Name |
|---|---|
| `uptime_kuma_data` | `managed_uptime_kuma_data` |

- Das Datenvolume enthält Monitore, Historie und Anwendungseinstellungen.
- Benachrichtigungs-Credentials können Teil des Anwendungszustands sein.
- Nach einem Restore Zustellung und aktive Monitore kontrollieren, damit Fehler nicht unbemerkt bleiben.

Im Manager **Backups / Import / Export** öffnen und Stack, Service und Mounts auswählen.
Alle benötigten Services berücksichtigen; eine einzelne Service-Auswahl ist kein vollständiges Stack-Backup.
Der Manager hält betroffene Schreiber für Mount-Sicherungen an.
Konfiguration kann zusätzlich mit `age` verschlüsselt gesichert werden.
Vor einer Wiederherstellung Ziel-Mounts und vorhandene Daten prüfen.

## Wenn etwas nicht funktioniert

| Beobachtung | Zuerst prüfen |
|---|---|
| Monitor meldet gesund trotz Loginseite | Erwarteten Inhalt oder geeigneten internen Endpunkt prüfen. |
| Interner Hostname nicht auflösbar | Gemeinsames Docker-Netz und tatsächlichen Servicenamen prüfen. |
| Keine Benachrichtigung | Kanal-Konfiguration und separaten Benachrichtigungstest prüfen. |
| Daten nach Neustart weg | Persistente Volume-Zuordnung kontrollieren. |

Für den Containerstatus und begrenzte Logs im Repository:

```bash
docker compose --project-directory compose/uptime-kuma --env-file compose/uptime-kuma/.env -p uptime-kuma -f compose/uptime-kuma/compose.yml ps
docker compose --project-directory compose/uptime-kuma --env-file compose/uptime-kuma/.env -p uptime-kuma -f compose/uptime-kuma/compose.yml logs --tail=80
```

Fehlt die `.env`, zuerst die Einrichtung abschließen.
Vor dem Weitergeben von Logs mögliche Zugangsdaten und persönliche Daten entfernen.

## Grenzen und weiterführende Dateien

Diese Seite beschreibt die vorhandene Konfiguration und ersetzt keinen Live-Test.
Ein erfolgreicher Compose-Check beweist weder SSO noch die vollständige Wiederherstellung.

- [Compose-Konfiguration](../../compose/uptime-kuma/compose.yml)
- [Stack-Metadaten und Hooks](../../compose/uptime-kuma/stack.py)
- [Gemeinsame Manager-Funktionen](../manager.md)
- [Ausstehende Betriebsprüfungen](../validierung.md)
