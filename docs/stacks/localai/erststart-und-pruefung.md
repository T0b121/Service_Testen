# LocalAI: Erststart und Prüfung

```bash
cd <PROJEKT_ROOT>/Compose/localai
docker compose up -d
./scripts/configure-authentik-oidc.sh
docker compose up -d --force-recreate localai
docker compose ps
```

Danach `https://localai.<DOMAIN>` öffnen. Der Klick auf die OIDC-Anmeldung
leitet zu Authentik und zurück. Mitglieder von `localai-users` dürfen sich
anmelden; Mitglieder von `localai-admins` zusätzlich verwalten.

Vor einem API-Einsatz einen separaten API-Schlüssel in LocalAI anlegen. Diesen
als Credential des jeweiligen Clients hinterlegen, nie einen persönlichen
Administrator-Schlüssel gemeinsam verwenden.
