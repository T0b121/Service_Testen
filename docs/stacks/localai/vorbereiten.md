# LocalAI: Vorbereiten

```bash
cd <PROJEKT_ROOT>/Compose/localai
cp .env.example .env
chmod 600 .env
./scripts/bootstrap-secrets.sh
docker compose config --quiet
```

In `.env` muss `LOCALAI_ADMIN_EMAIL` die E-Mail eines bestehenden
Authentik-Administrators enthalten. Das OIDC-Client-Secret wird ausschließlich
als lokale Docker-Secret-Datei abgelegt und nie in Git eingecheckt.
