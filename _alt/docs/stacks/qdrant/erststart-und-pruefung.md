# Qdrant-Stack: Erststart und Prüfung

## Start

```bash
cd <PROJEKT_ROOT>/Compose/qdrant
docker compose pull
docker compose up -d
docker compose ps
```

Erwartet wird `healthy`. Die Containeransicht darf ausschließlich
`6333-6334/tcp` anzeigen, niemals eine Hostbindung wie `0.0.0.0:6333->...`.

## Interne API und Schlüsselpflicht

Von einem berechtigten Container im gemeinsamen Netz:

```bash
curl -H 'api-key: <QDRANT_API_KEY>' http://qdrant:6333/collections
```

Die Antwort ist `200`. Derselbe Aufruf ohne Header muss `401` liefern. Der
eingerichtete Stack wurde genau so geprüft.

## Browserweg

`https://qdrant.<DOMAIN>/` muss ohne Authentik-Sitzung zu Authentik umleiten
und nach erfolgreicher Anmeldung zur UI unter `/dashboard/` führen. Der
Outpost-Ping muss `204` liefern:

```bash
curl -I https://qdrant.<DOMAIN>/
curl -I https://qdrant.<DOMAIN>/outpost.goauthentik.io/ping
```

Nach der Authentik-Anmeldung `https://qdrant.<DOMAIN>/dashboard` öffnen und
den lokalen `QDRANT_API_KEY` nur im vorgesehenen Qdrant-Web-UI-Eingabefeld
verwenden. Er wird weder über Traefik noch über die URL übertragen.

## Uptime Kuma

Der Monitor **Qdrant** (ID `12`) prüft `http://qdrant:6333/healthz` alle 60
Sekunden. Sein erster Heartbeat lieferte `200 - OK`.

Weiter mit [Betrieb](betrieb.md).
