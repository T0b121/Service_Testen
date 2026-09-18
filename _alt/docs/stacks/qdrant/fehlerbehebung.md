# Qdrant-Stack: Fehlerbehebung

## Dashboard fordert immer wieder eine Anmeldung

Prüfen, ob der Provider **Qdrant Access Provider** im `authentik Embedded
Outpost` liegt und ob der Benutzer Mitglied von `qdrant-users` ist. Der
Outpost-Pfad darf in Traefik nicht selbst die `authentik`-Middleware erhalten.

## Dashboard erhält 401

Die Authentik-Anmeldung ist dann erfolgreich, aber der Qdrant-API-Schlüssel
fehlt oder ist falsch. Den Wert aus der lokalen `Compose/qdrant/.env` im
Dashboard eingeben; weder schwächeren Schutz konfigurieren noch den Schlüssel
in eine URL schreiben.

## Container ist nicht healthy

```bash
cd <PROJEKT_ROOT>/Compose/qdrant
docker compose logs --tail=100 qdrant
docker compose ps
```

Der Healthcheck nutzt absichtlich Bash-TCP, weil das offizielle Image kein
`curl` oder `wget` enthält. Ein Healthcheck mit einem dieser nicht vorhandenen
Programme ist falsch.

## Interner Client erhält 401

Adresse, Netzwerkmitgliedschaft und `api-key`-Header prüfen. Ein
`qdrant_clients`-Mitglied verwendet `http://qdrant:6333`, nicht die öffentliche
Dashboard-Adresse.
