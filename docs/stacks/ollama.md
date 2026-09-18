# Ollama

[Alle Dienste](../dienste.md) · [Schnellstart](../../SCHNELLSTART.md)

## Was macht der Dienst?

Ollama führt lokal installierte Sprachmodelle aus.
Andere Anwendungen greifen über seine API darauf zu.
Im Projekt verwenden Open WebUI und LiteLLM dieses Backend.
Das persistente Volume hält die heruntergeladenen Modelle.
Ollama selbst ist hier keine zusätzliche Chat-Weboberfläche.

## Einordnung in diesem Repository

| Punkt | Konfiguration |
|---|---|
| Stack-ID | `ollama` |
| Browseradresse | `https://ollama.<DOMAIN>` |
| Direkte Abhängigkeiten | [core](core.md) |
| Anmeldung | Forward Auth; kein nativer SSO-Adapter in diesem Stack. |
| Deklarierte Dienstgruppen | `ollama-admins`, `ollama-users` |

`<DOMAIN>` steht für die bei der Einrichtung gewählte Basisdomain.
Abhängigkeiten werden vom Manager ergänzt; weitere indirekte Stacks können dazukommen.
Eine Dienstgruppe regelt den äußeren Zugang, nicht automatisch jede Berechtigung innerhalb der Anwendung.

## Bestandteile

| Compose-Service | Container-Image |
|---|---|
| `ollama` | `ollama/ollama:${OLLAMA_VERSION}` |

Image-Variablen werden aus der Stack-Konfiguration aufgelöst.
Die Tabelle beschreibt den Repository-Stand, keine Liste bereits gestarteter Container.

## Einrichten und starten

Den [Schnellstart](../../SCHNELLSTART.md) einmal für den Host durchführen.
Danach im Manager **Ersteinrichtung** beziehungsweise **Stack-Auswahl ändern** öffnen:

```bash
sudo .venv/bin/python compose/manage.py
```

`ollama` auswählen und die ermittelten Abhängigkeiten kontrollieren.
Vorhandene Werte werden wiederverwendet; neue Secrets gehören nicht in Git.
Erst nach erfolgreicher Einrichtung mit der Nutzung beginnen.

## Erste Nutzung

1. Den Stack über den Manager einrichten und den Dienststatus prüfen.
2. Im Ollama-Container die vorhandenen Modelle mit `ollama list` ansehen.
3. Für die mitgelieferte LiteLLM-Konfiguration beispielsweise `ollama pull qwen3:0.6b` ausführen.
4. Das installierte Modell mit einer kleinen Anfrage testen.
5. Danach in Open WebUI auswählen oder über den freigegebenen LiteLLM-Modellnamen ansprechen.

## Wichtige Einstellungen

| Einstellung | Bedeutung |
|---|---|
| `OLLAMA_VERSION` | Version des Modellservers. |
| `OLLAMA_KEEP_ALIVE` | Dauer, für die Modelle nach Anfragen geladen bleiben; Standard `5m`. |
| `DOMAIN` | Öffentliche Ollama-Subdomain. |

Die vollständigen Eingaben stehen in [`.env.example`](../../compose/ollama/.env.example).
Normale Werte im Manager über **Konfiguration bearbeiten** ändern.
Passwortwechsel sind keine bloßen Textänderungen: Datei und laufender Dienst müssen zusammenpassen.

## Besonderheiten dieser Konfiguration

- Der interne API-Zugang lautet `http://ollama:11434` für Container im passenden Netz.
- Der öffentliche Zugang liegt hinter Forward Auth und ist nicht automatisch für jeden API-Client nutzbar.
- Ein Containerstart lädt keine Modelle herunter.
- Die Compose-Datei enthält hier keine GPU-Gerätezuweisung; GPU-Unterstützung muss gesondert eingerichtet werden.
- `OLLAMA_KEEP_ALIVE` beeinflusst, wie lange ein Modell nach einer Anfrage geladen bleibt.
- Modelle mit unterschiedlicher Größe benötigen unterschiedlich viel Arbeitsspeicher; klein anfangen.

## Daten und Sicherung

| Volume-Schlüssel | Tatsächlicher Volume-Name |
|---|---|
| `ollama_data` | `managed_ollama_data` |

- Das Modellvolume enthält die installierten Modelldateien und deren lokale Zuordnung.
- Downloads sind häufig ersetzbar; eigene Modelle oder Modifikationen gesondert bewerten.
- Die Chat-Historie von Open WebUI liegt nicht in diesem Ollama-Volume.

Im Manager **Backups / Import / Export** öffnen und Stack, Service und Mounts auswählen.
Alle benötigten Services berücksichtigen; eine einzelne Service-Auswahl ist kein vollständiges Stack-Backup.
Der Manager hält betroffene Schreiber für Mount-Sicherungen an.
Konfiguration kann zusätzlich mit `age` verschlüsselt gesichert werden.
Vor einer Wiederherstellung Ziel-Mounts und vorhandene Daten prüfen.

## Wenn etwas nicht funktioniert

| Beobachtung | Zuerst prüfen |
|---|---|
| Keine Modelle vorhanden | Modell zunächst im Ollama-Dienst herunterladen. |
| Modellname unbekannt | Namen aus `ollama list` mit der Client-Konfiguration abgleichen. |
| Prozess wird beendet | Verfügbaren Speicher und Hostmeldungen prüfen. |
| Öffentliche API liefert Login-HTML | Äußere Authentifizierung berücksichtigen oder passenden internen Weg verwenden. |

Für den Containerstatus und begrenzte Logs im Repository:

```bash
docker compose --project-directory compose/ollama --env-file compose/ollama/.env -p ollama -f compose/ollama/compose.yml ps
docker compose --project-directory compose/ollama --env-file compose/ollama/.env -p ollama -f compose/ollama/compose.yml logs --tail=80
```

Fehlt die `.env`, zuerst die Einrichtung abschließen.
Vor dem Weitergeben von Logs mögliche Zugangsdaten und persönliche Daten entfernen.

## Grenzen und weiterführende Dateien

Diese Seite beschreibt die vorhandene Konfiguration und ersetzt keinen Live-Test.
Ein erfolgreicher Compose-Check beweist weder SSO noch die vollständige Wiederherstellung.

- [Compose-Konfiguration](../../compose/ollama/compose.yml)
- [Stack-Metadaten und Hooks](../../compose/ollama/stack.py)
- [Gemeinsame Manager-Funktionen](../manager.md)
- [Ausstehende Betriebsprüfungen](../validierung.md)
