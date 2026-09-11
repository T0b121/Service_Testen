# GitLab-Stack: Authentik einrichten

In Authentik einen OAuth2/OpenID Provider mit dem Namen `GitLab OIDC` anlegen.
Als Redirect URI exakt eintragen:

```text
https://gitlab.<DOMAIN>/users/auth/openid_connect/callback
```

Beim zugehörigen Authentik-Application-Eintrag muss der Slug `gitlab` sein,
weil GitLab den Issuer `https://auth.<DOMAIN>/application/o/gitlab/`
verwendet. Als Scopes mindestens `openid`, `profile` und `email` freigeben.
Den Zugriff auf eine Gruppe wie `gitlab-users` beschränken.

Danach das Client-Secret als alleinigen Inhalt in
`Compose/gitlab/secrets/gitlab_oidc_client_secret` schreiben. Die Client-ID
mit `GITLAB_OIDC_CLIENT_ID` in `.env` abgleichen. Keine Anführungs- oder
Leerzeichen mitkopieren.

Die Berechtigungen bleiben in Authentik. Die Gruppen `gitlab-users` und
`gitlab-admins` sind beide an die GitLab-Anwendung gebunden; Administratoren
sollten zusätzlich stets Mitglied von `gitlab-users` sein. Der lokale
Synchronisierungsdienst übersetzt die Mitgliedschaft anschließend in GitLab:

- `gitlab-users`: OIDC-Konto ist in GitLab aktiv.
- `gitlab-admins`: OIDC-Konto erhält zusätzlich GitLab-Administratorrechte.

Ein Konto muss sich zunächst einmal per OIDC in GitLab anmelden, damit GitLab
das lokale Konto anlegen kann. Danach übernimmt der Sync die Rechte spätestens
innerhalb von fünf Minuten und bestätigt auch neue, in GitLab wartende
OIDC-Konten. Der lokale `root`-Zugang bleibt ausschließlich ein
Notfallzugang und wird vom Sync nie verändert.

Weiter mit [Erststart und Prüfung](erststart-und-pruefung.md).
