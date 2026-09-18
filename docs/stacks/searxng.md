# SearXNG

[Alle Dienste](../dienste.md) · [Schnellstart](../../SCHNELLSTART.md)

## Was macht der Dienst?

SearXNG bündelt Suchanfragen an mehrere Suchmaschinen.
Die Oberfläche dient der interaktiven Suche im Browser.
Anwendungen können die freigegebenen Ausgabeformate für eigene Suchfunktionen nutzen.
Dieser Stack verwendet Valkey und separate Netze für interne Clients.
Suchmaschinen, Formate und Begrenzungen werden über Konfigurationsdateien gesteuert.

## Einordnung in diesem Repository

| Punkt | Konfiguration |
|---|---|
| Stack-ID | `searxng` |
| Browseradresse | `https://searxng.<DOMAIN>` |
| Direkte Abhängigkeiten | [core](core.md) |
| Anmeldung | Forward Auth; kein nativer SSO-Adapter in diesem Stack. |
| Deklarierte Dienstgruppen | `searxng-admins`, `searxng-users` |

`<DOMAIN>` steht für die bei der Einrichtung gewählte Basisdomain.
Abhängigkeiten werden vom Manager ergänzt; weitere indirekte Stacks können dazukommen.
Eine Dienstgruppe regelt den äußeren Zugang, nicht automatisch jede Berechtigung innerhalb der Anwendung.

## Bestandteile

| Compose-Service | Container-Image |
|---|---|
| `searxng` | `docker.io/searxng/searxng:${SEARXNG_VERSION}` |
| `searxng-valkey` | `docker.io/valkey/valkey:${VALKEY_VERSION}` |

Image-Variablen werden aus der Stack-Konfiguration aufgelöst.
Die Tabelle beschreibt den Repository-Stand, keine Liste bereits gestarteter Container.

## Einrichten und starten

Den [Schnellstart](../../SCHNELLSTART.md) einmal für den Host durchführen.
Danach im Manager **Ersteinrichtung** beziehungsweise **Stack-Auswahl ändern** öffnen:

```bash
sudo .venv/bin/python compose/manage.py
```

`searxng` auswählen und die ermittelten Abhängigkeiten kontrollieren.
Vorhandene Werte werden wiederverwendet; neue Secrets gehören nicht in Git.
Erst nach erfolgreicher Einrichtung mit der Nutzung beginnen.

## Erste Nutzung

1. Die Suchoberfläche öffnen und eine einfache Anfrage testen.
2. Prüfen, welche Suchmaschinen tatsächlich Ergebnisse liefern.
3. Für eine Anwendung den internen Suchzugang und das benötigte Ausgabeformat festlegen.
4. Eine einzelne automatisierte Anfrage testen, bevor ein großer Workflow zugreift.
5. Bei Änderungen der Suchkonfiguration Ergebnisqualität und Fehlerverhalten erneut prüfen.

## Wichtige Einstellungen

| Einstellung | Bedeutung |
|---|---|
| `SEARXNG_VERSION` | Version der Suchanwendung. |
| `SEARXNG_SECRET` | Vertrauliches Anwendungsgeheimnis. |
| `VALKEY_VERSION` | Version des unterstützenden Valkey-Dienstes. |
| `DOMAIN` | Öffentliche Suchadresse. |

Die vollständigen Eingaben stehen in [`.env.example`](../../compose/searxng/.env.example).
Normale Werte im Manager über **Konfiguration bearbeiten** ändern.
Passwortwechsel sind keine bloßen Textänderungen: Datei und laufender Dienst müssen zusammenpassen.

## Besonderheiten dieser Konfiguration

- `config/settings.yml` und `config/limiter.toml` werden schreibgeschützt eingebunden.
- Für interne Konsumenten ist der Netzwerkalias `searxng-internal` vorgesehen.
- Valkey unterstützt den Betrieb; er ist keine Datenbank sämtlicher Suchergebnisse.
- Der Stack deklariert kein natives SSO, sondern äußeren Schutz durch Forward Auth.
- Eine Abhängigkeit von SearXNG aktiviert die Suchfunktion in Open WebUI nicht automatisch.
- Ergebnisse und Verfügbarkeit hängen auch von den abgefragten Suchmaschinen ab.

## Daten und Sicherung

| Volume-Schlüssel | Tatsächlicher Volume-Name |
|---|---|
| `searxng_cache` | `managed_searxng_cache` |
| `searxng_valkey_data` | `managed_searxng_valkey_data` |

- Die beiden versionierten Konfigurationsdateien und das vertrauliche Secret berücksichtigen.
- Cache und Valkey-Daten können für Betriebskontinuität hilfreich sein, sind aber kein Archiv des Webs.
- Eigene Änderungen an den Konfigurationsdateien nachvollziehbar versionieren.

Im Manager **Backups / Import / Export** öffnen und Stack, Service und Mounts auswählen.
Alle benötigten Services berücksichtigen; eine einzelne Service-Auswahl ist kein vollständiges Stack-Backup.
Der Manager hält betroffene Schreiber für Mount-Sicherungen an.
Konfiguration kann zusätzlich mit `age` verschlüsselt gesichert werden.
Vor einer Wiederherstellung Ziel-Mounts und vorhandene Daten prüfen.

## Wenn etwas nicht funktioniert

| Beobachtung | Zuerst prüfen |
|---|---|
| Keine Ergebnisse | Betroffene Suchmaschinen und deren Erreichbarkeit prüfen. |
| Automatisierte Anfrage wird abgelehnt | Ausgabeformat, Limiter und aufrufendes Netz prüfen. |
| Client erhält Loginseite | Internen Zugriff und öffentlichen Forward-Auth-Weg unterscheiden. |
| Konfigurationsänderung wirkt nicht | Richtige eingebundene Datei und neu gestarteten Dienst prüfen. |

Für den Containerstatus und begrenzte Logs im Repository:

```bash
docker compose --project-directory compose/searxng --env-file compose/searxng/.env -p searxng -f compose/searxng/compose.yml ps
docker compose --project-directory compose/searxng --env-file compose/searxng/.env -p searxng -f compose/searxng/compose.yml logs --tail=80
```

Fehlt die `.env`, zuerst die Einrichtung abschließen.
Vor dem Weitergeben von Logs mögliche Zugangsdaten und persönliche Daten entfernen.

## Grenzen und weiterführende Dateien

Diese Seite beschreibt die vorhandene Konfiguration und ersetzt keinen Live-Test.
Ein erfolgreicher Compose-Check beweist weder SSO noch die vollständige Wiederherstellung.

- [Compose-Konfiguration](../../compose/searxng/compose.yml)
- [Stack-Metadaten und Hooks](../../compose/searxng/stack.py)
- [Gemeinsame Manager-Funktionen](../manager.md)
- [Ausstehende Betriebsprüfungen](../validierung.md)
