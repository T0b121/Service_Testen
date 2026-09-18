# Neo4j

[Alle Dienste](../dienste.md) · [Schnellstart](../../SCHNELLSTART.md)

## Was macht der Dienst?

Neo4j ist eine Graphdatenbank für Knoten, Beziehungen und ihre Eigenschaften.
Sie eignet sich für Daten, bei denen Verbindungen eine zentrale Rolle spielen.
Abfragen werden mit Cypher formuliert.
Der Stack enthält zusätzlich einen intern erreichbaren MCP-Dienst.
Die HTTP-Oberfläche und das Bolt-Datenbankprotokoll sind unterschiedliche Zugänge.

## Einordnung in diesem Repository

| Punkt | Konfiguration |
|---|---|
| Stack-ID | `neo4j` |
| Browseradresse | `https://neo4j.<DOMAIN>` |
| Direkte Abhängigkeiten | [core](core.md) |
| Anmeldung | Forward Auth; kein nativer SSO-Adapter in diesem Stack. |
| Deklarierte Dienstgruppen | `neo4j-admins`, `neo4j-users` |

`<DOMAIN>` steht für die bei der Einrichtung gewählte Basisdomain.
Abhängigkeiten werden vom Manager ergänzt; weitere indirekte Stacks können dazukommen.
Eine Dienstgruppe regelt den äußeren Zugang, nicht automatisch jede Berechtigung innerhalb der Anwendung.

## Bestandteile

| Compose-Service | Container-Image |
|---|---|
| `neo4j` | `neo4j:${NEO4J_VERSION}` |
| `neo4j-mcp` | `neo4j/mcp:${NEO4J_MCP_VERSION}` |

Image-Variablen werden aus der Stack-Konfiguration aufgelöst.
Die Tabelle beschreibt den Repository-Stand, keine Liste bereits gestarteter Container.

## Einrichten und starten

Den [Schnellstart](../../SCHNELLSTART.md) einmal für den Host durchführen.
Danach im Manager **Ersteinrichtung** beziehungsweise **Stack-Auswahl ändern** öffnen:

```bash
sudo .venv/bin/python compose/manage.py
```

`neo4j` auswählen und die ermittelten Abhängigkeiten kontrollieren.
Vorhandene Werte werden wiederverwendet; neue Secrets gehören nicht in Git.
Erst nach erfolgreicher Einrichtung mit der Nutzung beginnen.

## Erste Nutzung

1. Zuerst die Datenbank und ihren Healthcheck prüfen.
2. Über einen Client im passenden Netz eine Verbindung zur Datenbank herstellen.
3. Mit `RETURN 1 AS ok;` eine harmlose Cypher-Testabfrage ausführen.
4. Ein kleines Testmodell mit wenigen Knoten und Beziehungen aufbauen.
5. Erst danach Flowise, n8n oder einen MCP-Client mit passenden Credentials anbinden.

## Wichtige Einstellungen

| Einstellung | Bedeutung |
|---|---|
| `NEO4J_VERSION` | Version der Datenbank. |
| `NEO4J_MCP_VERSION` | Version des MCP-Dienstes. |
| `DOMAIN` | Öffentliche HTTP-Oberfläche; nicht gleichbedeutend mit Bolt-Freigabe. |

Die vollständigen Eingaben stehen in [`.env.example`](../../compose/neo4j/.env.example).
Normale Werte im Manager über **Konfiguration bearbeiten** ändern.
Passwortwechsel sind keine bloßen Textänderungen: Datei und laufender Dienst müssen zusammenpassen.

## Besonderheiten dieser Konfiguration

- APOC ist in der Compose-Konfiguration als Plugin vorgesehen.
- Die Datenbank-Credentials kommen aus `secrets/neo4j_auth`.
- Intern sind HTTP auf 7474 und Bolt auf 7687 vorgesehen; es gibt hier keine entsprechende Host-Portfreigabe.
- Traefik veröffentlicht die HTTP-Oberfläche, aber keinen automatisch konfigurierten externen Bolt-Zugang.
- Ein erfolgreicher Browseraufruf beweist daher nicht, dass ein externer Datenbankclient verbinden kann.
- `neo4j-mcp` liegt im Netz `neo4j_clients` und wird nicht als öffentliche Traefik-Anwendung angeboten.
- Der MCP-Dienst benötigt passend zu seiner Version eine funktionierende Datenbankanbindung; sein Containerstart allein weist diese nicht nach.

## Daten und Sicherung

| Volume-Schlüssel | Tatsächlicher Volume-Name |
|---|---|
| `neo4j_data` | `managed_neo4j_data` |
| `neo4j_logs` | `managed_neo4j_logs` |

- Das Datenvolume enthält den wesentlichen Datenbankbestand.
- Logs können Fehler erklären, stellen aber keine Datenbank wieder her.
- Bei externer Sicherung sicherstellen, dass keine Anwendung gleichzeitig in den wiederhergestellten Bestand schreibt.

Im Manager **Backups / Import / Export** öffnen und Stack, Service und Mounts auswählen.
Alle benötigten Services berücksichtigen; eine einzelne Service-Auswahl ist kein vollständiges Stack-Backup.
Der Manager hält betroffene Schreiber für Mount-Sicherungen an.
Konfiguration kann zusätzlich mit `age` verschlüsselt gesichert werden.
Vor einer Wiederherstellung Ziel-Mounts und vorhandene Daten prüfen.

## Wenn etwas nicht funktioniert

| Beobachtung | Zuerst prüfen |
|---|---|
| Webseite erreichbar, Datenbankverbindung scheitert | HTTP- und Bolt-Zugang getrennt prüfen. |
| Authentifizierung abgelehnt | Datenbankbenutzer und Secret-Inhalt prüfen. |
| MCP liefert keine Ergebnisse | MCP-Verbindung, Datenbankkonfiguration und Client-Berechtigung prüfen. |
| Abfrage ist langsam | Datenmodell, Datenmenge und geeignete Indizes untersuchen. |

Für den Containerstatus und begrenzte Logs im Repository:

```bash
docker compose --project-directory compose/neo4j --env-file compose/neo4j/.env -p neo4j -f compose/neo4j/compose.yml ps
docker compose --project-directory compose/neo4j --env-file compose/neo4j/.env -p neo4j -f compose/neo4j/compose.yml logs --tail=80
```

Fehlt die `.env`, zuerst die Einrichtung abschließen.
Vor dem Weitergeben von Logs mögliche Zugangsdaten und persönliche Daten entfernen.

## Grenzen und weiterführende Dateien

Diese Seite beschreibt die vorhandene Konfiguration und ersetzt keinen Live-Test.
Ein erfolgreicher Compose-Check beweist weder SSO noch die vollständige Wiederherstellung.

- [Compose-Konfiguration](../../compose/neo4j/compose.yml)
- [Stack-Metadaten und Hooks](../../compose/neo4j/stack.py)
- [Gemeinsame Manager-Funktionen](../manager.md)
- [Ausstehende Betriebsprüfungen](../validierung.md)
