# RustFS

[Alle Dienste](../dienste.md) · [Schnellstart](../../SCHNELLSTART.md)

## Was macht der Dienst?

RustFS stellt S3-kompatiblen Objektspeicher bereit.
Daten werden in Buckets unter Objektschlüsseln abgelegt.
In diesem Projekt nutzt insbesondere Langfuse diesen Speicher.
Der Stack enthält API und Verwaltungsoberfläche im selben Dienst.
Für die Browserverwaltung ist OIDC mit Authentik vorgesehen.

## Einordnung in diesem Repository

| Punkt | Konfiguration |
|---|---|
| Stack-ID | `rustfs` |
| Browseradresse | `https://s3.<DOMAIN>` |
| Direkte Abhängigkeiten | [core](core.md) |
| Anmeldung | Forward Auth und OIDC |
| Deklarierte Dienstgruppen | `rustfs-admins`, `rustfs-users` |

`<DOMAIN>` steht für die bei der Einrichtung gewählte Basisdomain.
Abhängigkeiten werden vom Manager ergänzt; weitere indirekte Stacks können dazukommen.
Eine Dienstgruppe regelt den äußeren Zugang, nicht automatisch jede Berechtigung innerhalb der Anwendung.

## Bestandteile

| Compose-Service | Container-Image |
|---|---|
| `rustfs` | `rustfs/rustfs:${RUSTFS_VERSION}` |

Image-Variablen werden aus der Stack-Konfiguration aufgelöst.
Die Tabelle beschreibt den Repository-Stand, keine Liste bereits gestarteter Container.

## Einrichten und starten

Den [Schnellstart](../../SCHNELLSTART.md) einmal für den Host durchführen.
Danach im Manager **Ersteinrichtung** beziehungsweise **Stack-Auswahl ändern** öffnen:

```bash
sudo .venv/bin/python compose/manage.py
```

`rustfs` auswählen und die ermittelten Abhängigkeiten kontrollieren.
Vorhandene Werte werden wiederverwendet; neue Secrets gehören nicht in Git.
Erst nach erfolgreicher Einrichtung mit der Nutzung beginnen.

## Erste Nutzung

1. Mit einer berechtigten Admin-Gruppe die Oberfläche unter `s3.<DOMAIN>` öffnen.
2. Vorhandene Buckets prüfen; der Einrichtungshook richtet den Langfuse-Bucket ein.
3. Einen kleinen Upload und anschließenden Download mit einem geeigneten Client testen.
4. Für Anwendungen eigene passende Credentials statt pauschal Root-Zugang verwenden.
5. Vor dem Löschen von Objekten die konsumierende Anwendung und ihre Referenzen prüfen.

## Wichtige Einstellungen

| Einstellung | Bedeutung |
|---|---|
| `RUSTFS_VERSION` | Version des Objektspeichers. |
| `RUSTFS_OIDC_CLIENT_ID` | Clientkennung der Konsole. |
| `DOMAIN` | Öffentliche S3- und Konsolenadresse. |

Die vollständigen Eingaben stehen in [`.env.example`](../../compose/rustfs/.env.example).
Normale Werte im Manager über **Konfiguration bearbeiten** ändern.
Passwortwechsel sind keine bloßen Textänderungen: Datei und laufender Dienst müssen zusammenpassen.

## Besonderheiten dieser Konfiguration

- Die veröffentlichte Anwendung erlaubt derzeit `rustfs-admins`; die ebenfalls deklarierte Gruppe `rustfs-users` erhält dadurch nicht automatisch Zugang.
- OIDC verwendet in dieser Konfiguration die Policy `consoleAdmin`; es ist kein fertiges Modell für viele eingeschränkte Mandanten.
- Der Einrichtungshook erstellt den Bucket `langfuse`, einen Dienstbenutzer und eine dazu passende Policy.
- Diese Provisionierung verwendet einen kurzlebigen `minio/mc`-Container im Netz `rustfs_clients`.
- Intern ist die S3-API unter `http://rustfs:9000` vorgesehen.
- Auch die öffentliche S3-Route liegt hinter Forward Auth; gewöhnliche S3-Clients können daran scheitern.
- S3-Objekte sind keine normalen lokalen Dateipfade für andere Container.

## Daten und Sicherung

| Volume-Schlüssel | Tatsächlicher Volume-Name |
|---|---|
| `rustfs_data` | `managed_rustfs_data` |

- Das RustFS-Datenvolume enthält die Objekte und den zugehörigen Dienstzustand.
- Langfuse-Datenbank und Objekte müssen bei einer Wiederherstellung zusammenpassen.
- Schlüsselmaterial zusätzlich verschlüsselt sichern; Root-Zugang nicht als Ersatz für jede Dienstidentität verteilen.

Im Manager **Backups / Import / Export** öffnen und Stack, Service und Mounts auswählen.
Alle benötigten Services berücksichtigen; eine einzelne Service-Auswahl ist kein vollständiges Stack-Backup.
Der Manager hält betroffene Schreiber für Mount-Sicherungen an.
Konfiguration kann zusätzlich mit `age` verschlüsselt gesichert werden.
Vor einer Wiederherstellung Ziel-Mounts und vorhandene Daten prüfen.

## Wenn etwas nicht funktioniert

| Beobachtung | Zuerst prüfen |
|---|---|
| Langfuse kann nicht schreiben | Bucket, Dienstschlüssel, Policy und internen Endpoint prüfen. |
| S3-Client erhält Login-HTML | Öffentliche Route und Forward Auth berücksichtigen. |
| OIDC-Nutzer erhält keinen Zugang | Die tatsächlich freigegebene Admin-Gruppe prüfen. |
| Einrichtungshook scheitert | RustFS-Logs, Client-Kompatibilität und Dienst-Credentials kontrollieren. |

Für den Containerstatus und begrenzte Logs im Repository:

```bash
docker compose --project-directory compose/rustfs --env-file compose/rustfs/.env -p rustfs -f compose/rustfs/compose.yml ps
docker compose --project-directory compose/rustfs --env-file compose/rustfs/.env -p rustfs -f compose/rustfs/compose.yml logs --tail=80
```

Fehlt die `.env`, zuerst die Einrichtung abschließen.
Vor dem Weitergeben von Logs mögliche Zugangsdaten und persönliche Daten entfernen.

## Grenzen und weiterführende Dateien

Diese Seite beschreibt die vorhandene Konfiguration und ersetzt keinen Live-Test.
Ein erfolgreicher Compose-Check beweist weder SSO noch die vollständige Wiederherstellung.

- [Compose-Konfiguration](../../compose/rustfs/compose.yml)
- [Stack-Metadaten und Hooks](../../compose/rustfs/stack.py)
- [Gemeinsame Manager-Funktionen](../manager.md)
- [Ausstehende Betriebsprüfungen](../validierung.md)
