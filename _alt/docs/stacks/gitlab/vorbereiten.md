# GitLab-Stack: Vorbereiten

`Compose/gitlab/.env` ist lokal und wird nicht eingecheckt. Vor dem ersten
Start müssen die beiden Initialsecrets unter `Compose/gitlab/secrets/`
existieren:

| Datei | Inhalt |
|---|---|
| `gitlab_initial_root_password` | einmaliges lokales GitLab-Root-Passwort |
| `gitlab_oidc_client_secret` | OIDC-Client-Secret aus Authentik |
| `authentik_gitlab_sync_api_token` | zunächst leere, später eingeschränkte Authentik-API-Secret-Datei |
| `gitlab_auth_sync_api_token` | zunächst leere, später GitLab-API-Secret-Datei |

Die Dateien werden als Docker Secrets eingehängt. Sie dürfen weder in Git
noch in Chat, Logs oder Screenshots erscheinen. `<+…>` steht für den Inhalt
einer Secret-Datei.

```bash
cd <PROJEKT_ROOT>/Compose/gitlab
mkdir -p secrets
chmod 700 secrets
printf '%s' '<+GITLAB_INITIAL_ROOT_PASSWORD>' > secrets/gitlab_initial_root_password
printf '%s' '<+GITLAB_OIDC_CLIENT_SECRET>' > secrets/gitlab_oidc_client_secret
install -m 600 /dev/null secrets/authentik_gitlab_sync_api_token
install -m 600 /dev/null secrets/gitlab_auth_sync_api_token
chmod 600 secrets/gitlab_initial_root_password secrets/gitlab_oidc_client_secret
docker compose config --quiet
```

Die Platzhalter ersetzen, nicht wörtlich speichern. Für das Root-Passwort ist
ein Passwortmanager-Wert mit mindestens 32 zufälligen Zeichen geeignet. Es ist
nur der Notfallzugang; die tägliche Anmeldung erfolgt über Authentik.

Der Host nutzt zusätzlich 12 GiB Swap als Puffer für kurzzeitige Lastspitzen.
Swap ersetzt keinen RAM und ist keine Freigabe für mehrere parallele Jobs.

Die zunächst leeren Sync-Dateien werden bei der Authentik-/GitLab-Einrichtung
befüllt. Der Authentik-Token ist auf das Lesen von Gruppen und Benutzern
begrenzt; der GitLab-Token darf in GitLab CE Administratorrechte und
Kontostatus setzen. Beide sind einjährige, lokale Secrets und niemals
Git-Dateien.

Weiter mit [Authentik einrichten](authentik-einrichten.md).
