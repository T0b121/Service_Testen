# Flowise-Stack: Erststart und Prüfung

## Start

```bash
cd <PROJEKT_ROOT>/Compose/flowise
docker compose pull
docker compose up -d
docker compose ps
```

`flowise` und `flowise-postgresql` müssen `healthy` sein. Es dürfen keine
Host-Port-Bindungen angezeigt werden.

## Interner Healthcheck

```bash
docker compose exec -T flowise curl -fsS http://127.0.0.1:3000/api/v1/ping
```

Erwartete Antwort: `pong`.

## Browser und Anmeldung

```bash
curl -I https://flowise.<DOMAIN>/
curl -I https://flowise.<DOMAIN>/outpost.goauthentik.io/ping
```

Ohne Authentik-Sitzung leitet der erste Aufruf zur Anmeldung um; der Outpost-
Ping liefert `204`. Nach der Authentik-Anmeldung erscheint die lokale
Flowise-Anmeldung beziehungsweise beim ersten Besuch die Registrierung. Den
lokalen Flowise-Administrator separat registrieren und danach einen erneuten
privaten Browser-Login testen.

Der Stack wurde mit erfolgreicher Flowise-Registrierung, lokalem Login und
vollständig geladenem Node-Katalog geprüft.

## Uptime Kuma

Der Monitor **Flowise** prüft `http://flowise:3000/api/v1/ping` alle 60
Sekunden. Er muss `200 - OK` melden.

Weiter mit [Betrieb](betrieb.md).
