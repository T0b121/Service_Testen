# Langfuse-Stack: Erststart und Prüfung

## Start

```bash
cd <PROJEKT_ROOT>/Compose/langfuse
docker compose pull
docker compose up -d
docker compose ps
```

Alle fünf Container müssen `healthy` sein: `langfuse`, `langfuse-worker`,
`langfuse-postgresql`, `langfuse-clickhouse` und `langfuse-valkey`.

## Interne Healthchecks

Langfuse bindet bewusst an die Docker-IP statt an Loopback. Daher wird im
Container der jeweilige Hostname verwendet:

```bash
docker compose exec -T langfuse sh -ec \
  'wget -q -O - "http://$HOSTNAME:3000/api/public/health?failIfDatabaseUnavailable=true"'
docker compose exec -T langfuse-worker sh -ec \
  'wget -q -O - "http://$HOSTNAME:3030/api/health"'
```

Erwartet werden `{"status":"OK","version":"4.30.0"}` und
`{"status":"ok"}`.

## Browser und SSO

```bash
curl -I https://langfuse.<DOMAIN>/
curl -I https://langfuse.<DOMAIN>/outpost.goauthentik.io/ping
```

Der erste Aufruf muss ohne Authentik-Sitzung zur Anmeldung umleiten; der Ping
liefert `204`. Danach in einem privaten Browserfenster die sichtbare
Authentik-Kachel **Langfuse Access** öffnen. Nach Forward Auth startet die
Kachel die native OIDC-Anmeldung. Nach deren Rückleitung muss Langfuse ohne
lokale Passwortanmeldung erreichbar sein.

Weiter mit [Betrieb](betrieb.md).
