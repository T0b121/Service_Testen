# Langfuse-Stack: Fehlerbehebung

## Web oder Worker bleibt `unhealthy`

Langfuse lauscht im Container auf dessen Docker-IP, nicht auf `127.0.0.1`.
Die Healthchecks müssen daher `http://$HOSTNAME:3000/...` beziehungsweise
`http://$HOSTNAME:3030/...` verwenden. Prüfen:

```bash
cd <PROJEKT_ROOT>/Compose/langfuse
docker compose ps
docker compose logs --tail=150 langfuse langfuse-worker
```

## Startfehler wegen `ENCRYPTION_KEY`

`LANGFUSE_ENCRYPTION_KEY` muss exakt 64 Hex-Zeichen haben. Neu erzeugen:

```bash
openssl rand -hex 32
```

Den alten Wert nur dann ersetzen, wenn die Instanz noch keine verschlüsselten
Integrationsdaten enthält. Nach produktiver Nutzung muss der bestehende Wert
aus dem Backup wiederhergestellt werden.

## Authentik-Anmeldung landet nicht in Langfuse

Prüfen, dass der Provider den Scope `email` enthält und die Redirect-URI exakt
`https://langfuse.<DOMAIN>/api/auth/callback/authentik` lautet. Außerdem müssen
die Authentik- und `LANGFUSE_ADMIN_EMAIL`-E-Mail übereinstimmen. Der sichtbare
Forward-Auth-Provider und der ausgeblendete OIDC-Provider brauchen jeweils die
aktive Gruppenbindung zu `langfuse-users`.

## Keine LiteLLM-Traces sichtbar

LiteLLM muss Mitglied von `langfuse_clients` sein und mit
`LANGFUSE_OTEL_HOST=http://langfuse:3000` laufen. Prüfen, dass die beiden
LiteLLM-Schlüssel mit dem Langfuse-Projekt `litellm` übereinstimmen, dann
LiteLLM neu erstellen und einen neuen Modellaufruf senden.
