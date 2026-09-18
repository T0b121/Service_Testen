# GitLab-Stack: Fehlerbehebung

## GitLab bleibt beim Start lange `starting`

Der erste Omnibus-Start dauert mehrere Minuten. Fortschritt prüfen:

```bash
cd <PROJEKT_ROOT>/Compose/gitlab
docker compose logs -f gitlab
```

Bei OOM- oder Speicherwarnungen zuerst `free -h` und `docker stats` prüfen.
Nicht mehrere CI-Jobs freischalten; falls nötig das lokale Modell entladen und
GitLab anschließend neu starten.

## OIDC-Login schlägt fehl

Issuer, Provider-Slug, Redirect URI und Client-ID müssen zusammenpassen:

```text
Issuer:       https://auth.<DOMAIN>/application/o/gitlab/
Redirect URI: https://gitlab.<DOMAIN>/users/auth/openid_connect/callback
```

Das Client-Secret muss vollständig und ohne `Basic`, `Bearer` oder zusätzliche
Leerzeichen in der Secret-Datei stehen. Nach einer Änderung:

```bash
docker compose up -d --force-recreate gitlab
```

## Runner nimmt keinen Job an

Prüfen, ob der Projekt-Runner online, geschützt und für den verwendeten Tag
freigegeben ist. Der Beispiel-Runner akzeptiert nur Jobs mit `tags: [docker]`.

```bash
docker compose logs --tail=100 gitlab-runner
docker compose exec gitlab-runner gitlab-runner verify
```
