# Qdrant

[Alle Dienste](../dienste.md) · [Schnellstart](../../SCHNELLSTART.md)

## Was macht der Dienst?

Qdrant speichert Vektoren und zugehörige Metadaten.
Eine typische Nutzung ist die Ähnlichkeitssuche für dokumentengestützte KI-Antworten.
Flowise oder n8n können Daten einlesen und später passende Treffer abfragen.
Qdrant erzeugt nicht automatisch die Embeddings für beliebige Dokumente.
Der Stack schützt seine API zusätzlich mit einem eigenen API-Schlüssel.

## Einordnung in diesem Repository

| Punkt | Konfiguration |
|---|---|
| Stack-ID | `qdrant` |
| Browseradresse | `https://qdrant.<DOMAIN>` |
| Direkte Abhängigkeiten | [core](core.md) |
| Anmeldung | Forward Auth; kein nativer SSO-Adapter in diesem Stack. |
| Deklarierte Dienstgruppen | `qdrant-admins`, `qdrant-users` |

`<DOMAIN>` steht für die bei der Einrichtung gewählte Basisdomain.
Abhängigkeiten werden vom Manager ergänzt; weitere indirekte Stacks können dazukommen.
Eine Dienstgruppe regelt den äußeren Zugang, nicht automatisch jede Berechtigung innerhalb der Anwendung.

## Bestandteile

| Compose-Service | Container-Image |
|---|---|
| `qdrant` | `qdrant/qdrant:${QDRANT_VERSION}` |

Image-Variablen werden aus der Stack-Konfiguration aufgelöst.
Die Tabelle beschreibt den Repository-Stand, keine Liste bereits gestarteter Container.

## Einrichten und starten

Den [Schnellstart](../../SCHNELLSTART.md) einmal für den Host durchführen.
Danach im Manager **Ersteinrichtung** beziehungsweise **Stack-Auswahl ändern** öffnen:

```bash
sudo .venv/bin/python compose/manage.py
```

`qdrant` auswählen und die ermittelten Abhängigkeiten kontrollieren.
Vorhandene Werte werden wiederverwendet; neue Secrets gehören nicht in Git.
Erst nach erfolgreicher Einrichtung mit der Nutzung beginnen.

## Erste Nutzung

1. Ein Embedding-Modell und eine passende Vektordimension festlegen.
2. In einem angebundenen Client den internen Qdrant-Endpoint und API-Schlüssel eintragen.
3. Eine Test-Collection mit passender Dimension und Distanzmetrik anlegen.
4. Wenige Testeinträge mit nachvollziehbaren Metadaten speichern.
5. Eine Suchanfrage mit demselben Embedding-Verfahren ausführen und Treffer prüfen.

## Wichtige Einstellungen

| Einstellung | Bedeutung |
|---|---|
| `QDRANT_VERSION` | Version der Vektordatenbank. |
| `QDRANT_API_KEY` | Vertraulicher Schlüssel für API-Zugriffe. |
| `DOMAIN` | Öffentliche Qdrant-Subdomain. |

Die vollständigen Eingaben stehen in [`.env.example`](../../compose/qdrant/.env.example).
Normale Werte im Manager über **Konfiguration bearbeiten** ändern.
Passwortwechsel sind keine bloßen Textänderungen: Datei und laufender Dienst müssen zusammenpassen.

## Besonderheiten dieser Konfiguration

- Die interne HTTP-API ist für verbundene Container über `http://qdrant:6333` erreichbar.
- Das Netz `qdrant_clients` verbindet die vorgesehenen Konsumenten.
- Die öffentliche HTTP-Route wird zusätzlich durch Forward Auth geschützt.
- Ein Qdrant-API-Key ersetzt keine Authentik-Anmeldung auf der öffentlichen Route.
- Ein Wechsel des Embedding-Modells kann eine neue Collection und erneutes Einlesen erfordern.
- Vektordaten sind nicht gleichbedeutend mit einem vollständigen Archiv aller Originaldokumente.

## Daten und Sicherung

| Volume-Schlüssel | Tatsächlicher Volume-Name |
|---|---|
| `qdrant_storage` | `managed_qdrant_storage` |

- Das Storage-Volume bewahrt die Qdrant-Daten.
- Originaldokumente und die zur Rekonstruktion verwendete Pipeline separat berücksichtigen.
- Die Manager-Sicherung ist ein Mount-Archiv mit angehaltenen Schreibern, kein automatisch erstellter Qdrant-Snapshot.

Im Manager **Backups / Import / Export** öffnen und Stack, Service und Mounts auswählen.
Alle benötigten Services berücksichtigen; eine einzelne Service-Auswahl ist kein vollständiges Stack-Backup.
Der Manager hält betroffene Schreiber für Mount-Sicherungen an.
Konfiguration kann zusätzlich mit `age` verschlüsselt gesichert werden.
Vor einer Wiederherstellung Ziel-Mounts und vorhandene Daten prüfen.

## Wenn etwas nicht funktioniert

| Beobachtung | Zuerst prüfen |
|---|---|
| Vektordimension passt nicht | Collection-Einstellung und Embedding-Ausgabe vergleichen. |
| API antwortet mit 401 | Qdrant-Schlüssel prüfen. |
| Öffentlicher Client bekommt Loginseite | Zusätzlichen Forward-Auth-Zugriff beachten. |
| Treffer sind unbrauchbar | Dokumentaufbereitung, Modell und Suchparameter prüfen. |

Für den Containerstatus und begrenzte Logs im Repository:

```bash
docker compose --project-directory compose/qdrant --env-file compose/qdrant/.env -p qdrant -f compose/qdrant/compose.yml ps
docker compose --project-directory compose/qdrant --env-file compose/qdrant/.env -p qdrant -f compose/qdrant/compose.yml logs --tail=80
```

Fehlt die `.env`, zuerst die Einrichtung abschließen.
Vor dem Weitergeben von Logs mögliche Zugangsdaten und persönliche Daten entfernen.

## Grenzen und weiterführende Dateien

Diese Seite beschreibt die vorhandene Konfiguration und ersetzt keinen Live-Test.
Ein erfolgreicher Compose-Check beweist weder SSO noch die vollständige Wiederherstellung.

- [Compose-Konfiguration](../../compose/qdrant/compose.yml)
- [Stack-Metadaten und Hooks](../../compose/qdrant/stack.py)
- [Gemeinsame Manager-Funktionen](../manager.md)
- [Ausstehende Betriebsprüfungen](../validierung.md)
