# Authentik für Paperless-ngx einrichten

`./scripts/configure-authentik-oidc.sh` legt die folgenden Objekte
idempotent an und aktualisiert den OIDC-Client bei erneutem Ausführen:

```text
paperless-users
paperless-admins
```

Die bestehende GitLab-Zuordnung wird beim ersten Lauf übernommen:
`gitlab-users` nach `paperless-users` und `gitlab-admins` nach
`paperless-admins`. Danach werden Berechtigungen direkt in Authentik über
diese Paperless-Gruppen verwaltet. Administratoren gehören in beide Gruppen.

Die Gruppen werden im OIDC-Token als `groups` übermittelt. Bei jedem Login
synchronisiert Paperless diese Gruppen; `paperless-admins` wird dabei auf die
Paperless-Administratorrolle abgebildet.

Das Skript legt die gleichnamigen lokalen Paperless-Gruppen ebenfalls an und
erteilt `paperless-users` die nötigen Dokument- und Oberflächenrechte.

Provider und Anwendung:

```text
Application: Paperless
Slug: paperless
Launch URL: https://paperless.<DOMAIN>/
Provider: OAuth2/OpenID Provider, confidential, Authorization Code
Redirect URI: https://paperless.<DOMAIN>/accounts/oidc/authentik/login/callback/
Scopes: openid, profile, email, groups
```

Der Zugriff auf die Anwendung ist auf `paperless-users` und
`paperless-admins` beschränkt. Der OIDC-Client ist nur für Paperless bestimmt;
sein Secret liegt ausschließlich in `Compose/paperless/secrets/`.
