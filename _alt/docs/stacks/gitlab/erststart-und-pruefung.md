# GitLab-Stack: Erststart und Prüfung

Nach dem Ausfüllen von `.env` und beiden Secret-Dateien starten:

```bash
cd <PROJEKT_ROOT>/Compose/gitlab
docker compose pull
docker compose up -d
docker compose ps
docker compose logs --tail=100 gitlab
```

Der erste GitLab-Start kann wegen Datenbankinitialisierung und `reconfigure`
mehrere Minuten dauern. Erst fortfahren, wenn der Healthcheck `healthy` zeigt.
Der Compose-One-Shot-Service `gitlab-security-settings` setzt anschließend
automatisch die datenbankbasierten Sicherheitseinstellungen.

Prüfpunkte:

1. `https://gitlab.<DOMAIN>` öffnet die GitLab-Anmeldung über TLS.
2. Der Button **Authentik** leitet zur Authentik-Anmeldung und zurück.
3. Der lokale Notfallzugang `root` funktioniert für die initiale Administration.
4. Ein OIDC-Konto in `gitlab-users` kann sich anmelden; eines in
   `gitlab-admins` erhält nach dem Sync Administratorrechte.
5. Ein Testprojekt lässt sich per HTTPS klonen.
6. Die Clone-Adresse ist eine HTTPS-Adresse; Git-over-SSH ist nicht freigegeben.
7. Die Hinweise zu offener Selbstregistrierung und zum Web-IDE-Single-Origin-
   Fallback erscheinen nicht mehr im GitLab-Dashboard.

## Runner

Der lokale Instance-Runner ist bereits registriert. Er akzeptiert nur Jobs mit
dem Tag `docker`, ausschließlich von geschützten Branches oder Tags und nie
ungetaggte Jobs. Er führt maximal einen Docker-Job mit vier CPUs, 4 GiB RAM und
256 MiB Shared Memory aus.

Den Befehl `gitlab-runner list` nicht für Statusprüfungen verwenden: Diese
Runner-Version gibt dabei den Authentifizierungstoken aus. Stattdessen im
GitLab-Adminbereich unter **CI/CD → Runners** den Status kontrollieren oder die
Containerlogs nutzen:

```bash
cd <PROJEKT_ROOT>/Compose/gitlab
docker compose logs --tail=100 gitlab-runner
```

Für eine Pipeline muss der betreffende Branch bzw. Tag in GitLab geschützt
sein und der Job `tags: [docker]` setzen.

Weiter mit [Betrieb](betrieb.md).
