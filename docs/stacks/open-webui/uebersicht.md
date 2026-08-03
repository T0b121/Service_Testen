# Open-WebUI-Stack: Übersicht

Der Stack stellt die Open-WebUI-Oberfläche für den vorhandenen Ollama-Dienst
bereit. Die öffentliche Adresse ist `https://webui.<DOMAIN>`. Benutzer melden
sich nativ per OIDC bei Authentik an; lokale Open-WebUI-Konten sind deaktiviert.
Dies ist die Standardkonfiguration. Die alternative Kombination aus Authentik
Forward Auth und lokalen Open-WebUI-Konten ist in
[Ohne OIDC einrichten](authentik-einrichten-ohne-oidc.md) beschrieben.

## Dienste

| Dienst | Zweck | Erreichbarkeit |
|---|---|---|
| `open-webui` | Browseroberfläche und Benutzerverwaltung für Modelle | extern: `https://webui.<DOMAIN>` über Traefik mit Authentik-OIDC; intern: `http://open-webui:8080` im Netzwerk `web` |
| `ollama` | Modell-API und Ausführung | intern für Open WebUI: `http://ollama:11434` |

## Architektur

```text
Browser
  -> Traefik :443
  -> Open WebUI :8080
  -> Authentik OIDC
  -> Ollama :11434

Weitere vertrauenswürdige Container im Netzwerk web
  -> http://ollama:11434
```

Open WebUI und Ollama haben keine Host-Portmappings. Nur Traefik veröffentlicht
TCP 80 und 443. Die Verbindung von Open WebUI zu Ollama bleibt vollständig im
externen Docker-Netzwerk `web`.

Browser-Anfragen akzeptiert Open WebUI nur von `https://webui.<DOMAIN>`; die
Compose-Variable `CORS_ALLOW_ORIGIN` verhindert die sonst offene Vorgabe `*`.

Open WebUI leitet nicht angemeldete Benutzer zu Authentik. Nach der OIDC-
Rückleitung erstellt oder aktualisiert Open WebUI das Konto anhand der
Authentik-Claims; die Rollen werden aus dem Claim `roles` übernommen.

## Rollen und Zugang

| Authentik-Gruppe | Bedeutung | Open-WebUI-Rolle |
|---|---|---|
| `openwebui-users` | Zugriff auf Open WebUI | `user` |
| `openwebui-admin` | administrative Verwaltung | `admin` |

Nur Mitglieder mindestens einer dieser Gruppen erhalten von Authentik eine
zulässige Rolle. Open WebUI legt das Benutzerkonto beim ersten OIDC-Login an.
Änderungen der Authentik-Gruppen wirken nach erneutem Anmelden.

## Voraussetzungen

- Der Core-Stack läuft mit Traefik und Authentik.
- Der Ollama-Stack läuft und ist im Netzwerk `web` erreichbar.
- Das externe Docker-Netzwerk `web` existiert.
- DNS für `webui.<DOMAIN>` zeigt auf den Server.
- TCP 80 und 443 sind extern erreichbar.
- Die lokale `.env` enthält die OIDC-Client-ID und das OIDC-Client-Secret.
- Der lokale Signierschlüssel wird vor dem Start angelegt.

## Persistente Daten

| Volume | Inhalt |
|---|---|
| `openwebui_data` | SQLite-Datenbank, hochgeladene Dateien, Einstellungen und lokale Open-WebUI-Daten |

Das Volume, der Signierschlüssel und die OIDC-Zugangsdaten sind für eine
Wiederherstellung erforderlich. Anwendung, Provider, Gruppen, Bindings und das
Rollen-Scope-Mapping liegen im Authentik-PostgreSQL-Backup des Core-Stacks.

Weiter mit:

- [Vorbereiten](vorbereiten.md)
- [Authentik einrichten](authentik-einrichten.md)
- [Ohne OIDC einrichten (Alternative)](authentik-einrichten-ohne-oidc.md)
- [Erststart und Prüfung](erststart-und-pruefung.md)
- [Betrieb](betrieb.md)
