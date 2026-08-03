# Open-WebUI-Stack: Übersicht

Der Stack stellt die Open-WebUI-Oberfläche für den vorhandenen Ollama-Dienst
bereit. Die öffentliche Adresse ist `https://webui.<DOMAIN>`. Der äußere
Zugriff wird durch Authentik Forward Auth geschützt; Open WebUI verwendet
zunächst lokale Konten und Passwörter.

## Dienste

| Dienst | Zweck | Erreichbarkeit |
|---|---|---|
| `open-webui` | Browseroberfläche und Benutzerverwaltung für Modelle | extern: `https://webui.<DOMAIN>` über Traefik und Authentik Forward Auth; intern: `http://open-webui:8080` im Netzwerk `web` |
| `ollama` | Modell-API und Ausführung | intern für Open WebUI: `http://ollama:11434` |

## Architektur

```text
Browser
  -> Traefik :443
  -> Authentik Forward Auth
  -> Open WebUI :8080
  -> Ollama :11434

Weitere vertrauenswürdige Container im Netzwerk web
  -> http://ollama:11434
```

Open WebUI und Ollama haben keine Host-Portmappings. Nur Traefik veröffentlicht
TCP 80 und 443. Die Verbindung von Open WebUI zu Ollama bleibt vollständig im
externen Docker-Netzwerk `web`.

Browser-Anfragen akzeptiert Open WebUI nur von `https://webui.<DOMAIN>`; die
Compose-Variable `CORS_ALLOW_ORIGIN` verhindert die sonst offene Vorgabe `*`.

Die zwei Anmeldeschichten haben getrennte Aufgaben: Authentik beschränkt, wer
die Weboberfläche überhaupt erreicht; Open WebUI ordnet danach lokale Konten
und Rollen zu. Eine spätere, eigene Umstellung auf natives OIDC ist möglich,
aber nicht Teil dieses ersten Betriebszustands.

## Rollen und Zugang

| Authentik-Gruppe | Bedeutung | Open-WebUI-Rolle |
|---|---|---|
| `openwebui-users` | Zugang zur Login-Seite | keine automatische lokale Rolle |
| `openwebui-admin` | Zugang zur Login-Seite für die Ersteinrichtung | keine automatische lokale Rolle |

Nur Mitglieder mindestens einer dieser Gruppen passieren Authentik. Der erste
lokale Open-WebUI-Benutzer wird zum Administrator; weitere lokale Konten werden
in Open WebUI verwaltet. Änderungen der Authentik-Gruppen wirken nach erneutem
Anmelden.

## Voraussetzungen

- Der Core-Stack läuft mit Traefik und Authentik.
- Der Ollama-Stack läuft und ist im Netzwerk `web` erreichbar.
- Das externe Docker-Netzwerk `web` existiert.
- DNS für `webui.<DOMAIN>` zeigt auf den Server.
- TCP 80 und 443 sind extern erreichbar.
- Zwei lokale Secret-Dateien werden vor dem Start angelegt.
- Für die Ersteinrichtung ist zunächst nur das Authentik-Administratorkonto in
  `openwebui-admin` erforderlich.

## Persistente Daten

| Volume | Inhalt |
|---|---|
| `openwebui_data` | SQLite-Datenbank, hochgeladene Dateien, Einstellungen und lokale Open-WebUI-Daten |

Das Volume und beide Secret-Dateien sind für eine Wiederherstellung erforderlich.
Die Proxy-Anwendung, Gruppen und Bindings liegen im Authentik-PostgreSQL-Backup
des Core-Stacks.

Weiter mit:

- [Vorbereiten](vorbereiten.md)
- [Authentik einrichten](authentik-einrichten.md)
- [Erststart und Prüfung](erststart-und-pruefung.md)
- [Betrieb](betrieb.md)
