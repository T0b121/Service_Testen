# Jellyfin

[Alle Dienste](../dienste.md) · [Schnellstart](../../SCHNELLSTART.md)

## Was macht der Dienst?

Jellyfin verwaltet eine persönliche Medienbibliothek und spielt deren Inhalte ab.
Bibliotheken können etwa Filme, Serien und Musik enthalten.
Der Stack speichert Serverkonfiguration, Cache und Medien in getrennten Volumes.
Ein gemeinsames Medienvolume kann auch von Nextcloud verwendet werden.
Die konkrete Client-Nutzung muss mit dem vorgeschalteten Forward Auth getestet werden.

## Einordnung in diesem Repository

| Punkt | Konfiguration |
|---|---|
| Stack-ID | `jellyfin` |
| Browseradresse | `https://jellyfin.<DOMAIN>` |
| Direkte Abhängigkeiten | [core](core.md) |
| Anmeldung | Forward Auth; kein nativer SSO-Adapter in diesem Stack. |
| Deklarierte Dienstgruppen | `jellyfin-admins`, `jellyfin-users` |

`<DOMAIN>` steht für die bei der Einrichtung gewählte Basisdomain.
Abhängigkeiten werden vom Manager ergänzt; weitere indirekte Stacks können dazukommen.
Eine Dienstgruppe regelt den äußeren Zugang, nicht automatisch jede Berechtigung innerhalb der Anwendung.

## Bestandteile

| Compose-Service | Container-Image |
|---|---|
| `jellyfin` | `jellyfin/jellyfin:${JELLYFIN_VERSION}` |

Image-Variablen werden aus der Stack-Konfiguration aufgelöst.
Die Tabelle beschreibt den Repository-Stand, keine Liste bereits gestarteter Container.

## Einrichten und starten

Den [Schnellstart](../../SCHNELLSTART.md) einmal für den Host durchführen.
Danach im Manager **Ersteinrichtung** beziehungsweise **Stack-Auswahl ändern** öffnen:

```bash
sudo .venv/bin/python compose/manage.py
```

`jellyfin` auswählen und die ermittelten Abhängigkeiten kontrollieren.
Vorhandene Werte werden wiederverwendet; neue Secrets gehören nicht in Git.
Erst nach erfolgreicher Einrichtung mit der Nutzung beginnen.

## Erste Nutzung

1. Die Weboberfläche öffnen und den Jellyfin-Einrichtungsdialog abschließen.
2. Eine Bibliothek anlegen und den im Container eingebundenen Medienpfad auswählen.
3. Eine kleine Testdatei bereitstellen und die Bibliothek einlesen lassen.
4. Die Wiedergabe im Browser prüfen, bevor große Bestände importiert werden.
5. Weitere Clients einzeln testen; ein funktionierender Browser beweist keinen funktionierenden TV-Client.

## Wichtige Einstellungen

| Einstellung | Bedeutung |
|---|---|
| `JELLYFIN_VERSION` | Version des Medienservers. |
| `DOMAIN` | Öffentliche Jellyfin-Adresse. |

Die vollständigen Eingaben stehen in [`.env.example`](../../compose/jellyfin/.env.example).
Normale Werte im Manager über **Konfiguration bearbeiten** ändern.
Passwortwechsel sind keine bloßen Textänderungen: Datei und laufender Dienst müssen zusammenpassen.

## Besonderheiten dieser Konfiguration

- Der Stack enthält keinen nativen Authentik-SSO-Adapter für Jellyfin.
- Authentik schützt den Eingang; Jellyfin kann zusätzlich eine eigene Anmeldung verlangen.
- Die allgemeine Vorgabe „nur SSO“ für Open WebUI ändert diesen Jellyfin-Stack nicht.
- Das Medienvolume heißt physisch `managed_jellyfin_media`; Jellyfin sieht es schreibgeschützt unter `/media`.
- Die Compose-Datei richtet keine automatische GPU-Durchreichung für Transcoding ein.
- Ein Medienbibliothekseintrag kopiert nicht automatisch Dateien in das Medienvolume.

## Daten und Sicherung

| Volume-Schlüssel | Tatsächlicher Volume-Name |
|---|---|
| `jellyfin_config` | `managed_jellyfin_config` |
| `jellyfin_cache` | `managed_jellyfin_cache` |
| `jellyfin_media` | `managed_jellyfin_media` |

- Konfiguration und Medien sind wichtiger als ein jederzeit neu aufbaubarer Cache.
- Bei gemeinsamem Medienvolume kann eine Sicherung auch andere Container anhalten.
- Medienbestand und Nextcloud-Zugriff gemeinsam planen, damit kein Schreibvorgang übersehen wird.

Im Manager **Backups / Import / Export** öffnen und Stack, Service und Mounts auswählen.
Alle benötigten Services berücksichtigen; eine einzelne Service-Auswahl ist kein vollständiges Stack-Backup.
Der Manager hält betroffene Schreiber für Mount-Sicherungen an.
Konfiguration kann zusätzlich mit `age` verschlüsselt gesichert werden.
Vor einer Wiederherstellung Ziel-Mounts und vorhandene Daten prüfen.

## Wenn etwas nicht funktioniert

| Beobachtung | Zuerst prüfen |
|---|---|
| Bibliothek bleibt leer | Pfad im Container und tatsächlich vorhandene Dateien vergleichen. |
| Wiedergabe stockt | Codec, Transcoding-Last, CPU und Netzwerk prüfen. |
| Client bekommt HTML statt API-Antwort | Möglicherweise greift die vorgeschaltete Authentik-Anmeldung. |
| Medien sind nicht lesbar | Dateirechte auf dem gemeinsam verwendeten Volume prüfen. |

Für den Containerstatus und begrenzte Logs im Repository:

```bash
docker compose --project-directory compose/jellyfin --env-file compose/jellyfin/.env -p jellyfin -f compose/jellyfin/compose.yml ps
docker compose --project-directory compose/jellyfin --env-file compose/jellyfin/.env -p jellyfin -f compose/jellyfin/compose.yml logs --tail=80
```

Fehlt die `.env`, zuerst die Einrichtung abschließen.
Vor dem Weitergeben von Logs mögliche Zugangsdaten und persönliche Daten entfernen.

## Grenzen und weiterführende Dateien

Diese Seite beschreibt die vorhandene Konfiguration und ersetzt keinen Live-Test.
Ein erfolgreicher Compose-Check beweist weder SSO noch die vollständige Wiederherstellung.

- [Compose-Konfiguration](../../compose/jellyfin/compose.yml)
- [Stack-Metadaten und Hooks](../../compose/jellyfin/stack.py)
- [Gemeinsame Manager-Funktionen](../manager.md)
- [Ausstehende Betriebsprüfungen](../validierung.md)
