# GitLab-Stack: Backup und Wiederherstellung

Zu sichern sind die Docker-Volumes `gitlab_config`, `gitlab_logs` und
`gitlab_data` sowie beide lokalen Secret-Dateien. `gitlab_data` enthält
Repositories, Uploads und die integrierte Datenbank.

Für einen konsistenten GitLab-eigenen Datenexport vor einem Upgrade:

```bash
cd <PROJEKT_ROOT>/Compose/gitlab
docker compose exec gitlab gitlab-backup create
```

Die Konfiguration und `gitlab-secrets.json` liegen im Volume `gitlab_config`
und müssen zusammen mit dem Backup gesichert werden. Ein Restore erfolgt nur
bei angehaltenem GitLab und mit derselben GitLab-Hauptversion.

Sobald der wiederhergestellte Container wieder den Status `healthy` erreicht,
die datenbankbasierten Sicherheitswerte erneut anwenden:

```bash
cd <PROJEKT_ROOT>/Compose/gitlab
./scripts/apply-security-settings.sh
```
