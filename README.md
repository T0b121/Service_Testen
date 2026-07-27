# Serverdienste-Dokumentation

Diese Dokumentation beschreibt die gemeinsame Serverbasis und die einzelnen Docker-Compose-Stacks dieses Repositorys.

`<DOMAIN>` steht überall für die in der lokalen `.env` konfigurierte Basisdomain.  
`<PROJEKT_ROOT>` bezeichnet das Root-Verzeichnis des Git-Repositorys, in dem `README.md`, `.gitignore`, `Compose/` und `docs/` liegen.

Platzhalter in spitzen Klammern sind vor der Ausführung zu ersetzen. Sie sind keine gültige Shell-Syntax. Beispiel: Aus `auth.<DOMAIN>` wird mit dem Wert aus `DOMAIN=` die tatsächliche Authentik-Adresse.

## Stacks

| Stack | Enthaltene Dienste | Öffentliche Endpunkte | Vorausgesetzte Stacks | Compose-Verzeichnis |
|---|---|---|---|---|
| `core` | Traefik, Authentik Server, Authentik Worker, PostgreSQL | `https://auth.<DOMAIN>`<br>`https://proxy.<DOMAIN>/dashboard/` | Keine | `Compose/core/` |

### Hinweise zum Core-Stack

- Nur Traefik veröffentlicht Host-Ports: TCP 80 und 443.
- Authentik ist über Traefik erreichbar.
- PostgreSQL und Authentik Worker sind ausschließlich intern erreichbar.
- Das Traefik-Dashboard wird durch Authentik geschützt.
- `https://proxy.<DOMAIN>/` darf absichtlich `404 page not found` liefern. Der vorgesehene Pfad lautet `/dashboard/`.
- Während Aufbau und Prüfung wird Let’s Encrypt Staging verwendet.

## Empfohlene Reihenfolge

1. [Server vorbereiten](docs/server/vorbereiten.md)
2. [Server konfigurieren](docs/server/konfigurieren.md)
3. [Projektkonventionen lesen](docs/projekt-konventionen.md)
4. [Core-Stack überblicken](docs/stacks/core/uebersicht.md)
5. [Core-Stack vorbereiten](docs/stacks/core/vorbereiten.md)
6. [Core-Stack erstmals starten und prüfen](docs/stacks/core/erststart-und-pruefung.md)
7. [Authentik für das Traefik-Dashboard einrichten](docs/stacks/core/authentik-einrichten.md)

## Dokumentation

### Allgemein

- [Projektkonventionen](docs/projekt-konventionen.md)
- [TLS und Zertifikate](docs/tls-und-zertifikate.md)
- [Backup und Wiederherstellung](docs/backup-und-wiederherstellung.md)
- [Wartung und Updates](docs/wartung-und-updates.md)

### Server

- [Server vorbereiten](docs/server/vorbereiten.md)
- [Server konfigurieren](docs/server/konfigurieren.md)
- [Serversicherheit](docs/server/sicherheit.md)
- [Server-Fehlerbehebung](docs/server/fehlerbehebung.md)

### Stack `core`

- [Übersicht](docs/stacks/core/uebersicht.md)
- [Vorbereiten](docs/stacks/core/vorbereiten.md)
- [Erststart und Prüfung](docs/stacks/core/erststart-und-pruefung.md)
- [Authentik einrichten](docs/stacks/core/authentik-einrichten.md)
- [Authentik verwalten](docs/stacks/core/authentik-verwaltung.md)
- [Betrieb](docs/stacks/core/betrieb.md)
- [Backup und Wiederherstellung](docs/stacks/core/backup-und-wiederherstellung.md)
- [Fehlerbehebung](docs/stacks/core/fehlerbehebung.md)
