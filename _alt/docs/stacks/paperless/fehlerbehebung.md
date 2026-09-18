# Paperless-ngx: Fehlerbehebung

## Keine Authentik-Anmeldung sichtbar

```bash
cd <PROJEKT_ROOT>/Compose/paperless
./scripts/configure-authentik-oidc.sh
docker compose up -d --force-recreate paperless
```

Danach die Paperless-Loginseite neu laden. Prüfe in Authentik die Mitgliedschaft
in `paperless-users` oder `paperless-admins`.

## Dokument bleibt in der Warteschlange

```bash
docker compose logs --tail=200 paperless
```

OCR- und Dateiformatfehler stehen dort beim jeweiligen Consumer-Job. Keine
Dokumente direkt in PostgreSQL verändern; Metadaten werden ausschließlich über
Paperless selbst oder dessen API korrigiert.
