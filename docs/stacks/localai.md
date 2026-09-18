# LocalAI

[Alle Dienste](../dienste.md) · [Schnellstart](../../SCHNELLSTART.md)

## Was macht der Dienst?

LocalAI stellt lokal betriebene KI-Modelle über APIs bereit.
Die Weboberfläche hilft beim Verwalten der Modellinstallation.
Welche Aufgaben möglich sind, hängt von den installierten Modellen und Backends ab.
Dieser Stack bewahrt Modelle, Konfiguration und Anwendungsdaten in Volumes auf.
Er kann als Backend für ein Gateway wie LiteLLM dienen.

## Einordnung in diesem Repository

| Punkt | Konfiguration |
|---|---|
| Stack-ID | `localai` |
| Browseradresse | `https://localai.<DOMAIN>` |
| Direkte Abhängigkeiten | [core](core.md) |
| Anmeldung | Forward Auth und OIDC |
| Deklarierte Dienstgruppen | `localai-admins`, `localai-users` |

`<DOMAIN>` steht für die bei der Einrichtung gewählte Basisdomain.
Abhängigkeiten werden vom Manager ergänzt; weitere indirekte Stacks können dazukommen.
Eine Dienstgruppe regelt den äußeren Zugang, nicht automatisch jede Berechtigung innerhalb der Anwendung.

## Bestandteile

| Compose-Service | Container-Image |
|---|---|
| `localai` | `localai/localai:${LOCALAI_VERSION}` |

Image-Variablen werden aus der Stack-Konfiguration aufgelöst.
Die Tabelle beschreibt den Repository-Stand, keine Liste bereits gestarteter Container.

## Einrichten und starten

Den [Schnellstart](../../SCHNELLSTART.md) einmal für den Host durchführen.
Danach im Manager **Ersteinrichtung** beziehungsweise **Stack-Auswahl ändern** öffnen:

```bash
sudo .venv/bin/python compose/manage.py
```

`localai` auswählen und die ermittelten Abhängigkeiten kontrollieren.
Vorhandene Werte werden wiederverwendet; neue Secrets gehören nicht in Git.
Erst nach erfolgreicher Einrichtung mit der Nutzung beginnen.

## Erste Nutzung

1. Die LocalAI-Weboberfläche über die eigene Subdomain öffnen.
2. Mit Authentik anmelden und die installierten Modelle prüfen.
3. Ein zur vorhandenen Hardware passendes kleines Modell installieren.
4. Das Modell zuerst direkt in LocalAI testen.
5. Danach den passenden Modellnamen und Endpoint in der konsumierenden Anwendung konfigurieren.

## Wichtige Einstellungen

| Einstellung | Bedeutung |
|---|---|
| `LOCALAI_VERSION` | Version des LocalAI-Images. |
| `LOCALAI_ADMIN_EMAIL` | Initiale Administrator-Mailadresse. |
| `DOMAIN` | Öffentliche LocalAI-Adresse. |

Die vollständigen Eingaben stehen in [`.env.example`](../../compose/localai/.env.example).
Normale Werte im Manager über **Konfiguration bearbeiten** ändern.
Passwortwechsel sind keine bloßen Textänderungen: Datei und laufender Dienst müssen zusammenpassen.

## Besonderheiten dieser Konfiguration

- Der Stack deklariert OIDC mit der festen Client-ID `localai` und übergibt das Client-Secret aus einer Secret-Datei.
- Die Zahl der CPU-Threads wird beim Containerstart aus `nproc` bestimmt.
- Ein heruntergeladenes Modell ist nicht automatisch als LiteLLM-Modell freigegeben.
- Bild-, Audio- und Sprachmodelle benötigen jeweils passende Backends; ein Dateidownload allein genügt nicht.
- LocalAI ist kein gemeinsamer Modell-Dateiserver für jede beliebige ComfyUI-Node.
- Die hier beschriebene Compose-Datei aktiviert keine automatische GPU-Durchreichung.

## Daten und Sicherung

| Volume-Schlüssel | Tatsächlicher Volume-Name |
|---|---|
| `localai_models` | `managed_localai_models` |
| `localai_data` | `managed_localai_data` |
| `localai_configuration` | `managed_localai_configuration` |
| `localai_backends` | `managed_localai_backends` |

- Modelldateien, Konfiguration und LocalAI-Daten gemeinsam berücksichtigen.
- Große Modelle können erneut herunterladbar sein; eigene Konfigurationen und Daten dagegen nicht unbedingt.
- OIDC-Secret und sonstige Zugangsdaten verschlüsselt sichern.

Im Manager **Backups / Import / Export** öffnen und Stack, Service und Mounts auswählen.
Alle benötigten Services berücksichtigen; eine einzelne Service-Auswahl ist kein vollständiges Stack-Backup.
Der Manager hält betroffene Schreiber für Mount-Sicherungen an.
Konfiguration kann zusätzlich mit `age` verschlüsselt gesichert werden.
Vor einer Wiederherstellung Ziel-Mounts und vorhandene Daten prüfen.

## Wenn etwas nicht funktioniert

| Beobachtung | Zuerst prüfen |
|---|---|
| Modell lädt nicht | Modellformat, Backend-Konfiguration, RAM und freien Speicher prüfen. |
| Antworten sind langsam | Modellgröße und CPU-Betrieb berücksichtigen. |
| SSO-Rückleitung scheitert | Client-ID, Domain und OIDC-Callback vergleichen. |
| LiteLLM sieht das Modell nicht | Gateway-Konfiguration separat kontrollieren. |

Für den Containerstatus und begrenzte Logs im Repository:

```bash
docker compose --project-directory compose/localai --env-file compose/localai/.env -p localai -f compose/localai/compose.yml ps
docker compose --project-directory compose/localai --env-file compose/localai/.env -p localai -f compose/localai/compose.yml logs --tail=80
```

Fehlt die `.env`, zuerst die Einrichtung abschließen.
Vor dem Weitergeben von Logs mögliche Zugangsdaten und persönliche Daten entfernen.

## Grenzen und weiterführende Dateien

Diese Seite beschreibt die vorhandene Konfiguration und ersetzt keinen Live-Test.
Ein erfolgreicher Compose-Check beweist weder SSO noch die vollständige Wiederherstellung.

- [Compose-Konfiguration](../../compose/localai/compose.yml)
- [Stack-Metadaten und Hooks](../../compose/localai/stack.py)
- [Gemeinsame Manager-Funktionen](../manager.md)
- [Ausstehende Betriebsprüfungen](../validierung.md)
