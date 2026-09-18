# GitLab-Stack: Betrieb

## Ressourcenmodell

GitLab darf maximal 8 GiB RAM und sechs CPUs nutzen. Typisch benötigt der
Einzelbetrieb im Leerlauf etwa 4–7 GiB; Git-Aktionen, größere Repositories und
Updates können kurzfristig mehr Druck erzeugen. Die 12 GiB Swap verhindern
einen sofortigen OOM-Abbruch, machen unter echter Speichernot aber alles
langsamer.

Der Runner selbst ist klein begrenzt. Er führt höchstens einen Job aus; jedem
Job stehen maximal 4 GiB RAM, vier CPUs und 256 MiB Shared Memory zu. Vor
speicherintensiven LLM-Aufgaben oder großen Builds keine CI-Jobs gleichzeitig
starten.

```bash
free -h
docker stats --no-stream gitlab gitlab-runner
cd <PROJEKT_ROOT>/Compose/gitlab
docker compose ps
```

## Authentik-Berechtigungssynchronisierung

`gitlab-auth-sync` ist Teil des normalen Compose-Starts. Es verwendet zwei
getrennte, jährlich ablaufende Secrets: einen auf `view_group` und `view_user`
beschränkten Authentik-Servicekonto-Token sowie einen GitLab-Admin-API-Token.
Nur der zweite braucht administrative Rechte, weil GitLab CE keine native
OIDC-Gruppen-zu-Administrator-Zuordnung bietet.

```bash
cd <PROJEKT_ROOT>/Compose/gitlab
docker compose logs --tail=100 gitlab-auth-sync
```

Ein erfolgreicher Lauf meldet nur Zählwerte, keine Token oder personenbezogenen
Attribute. Bei einem Fehler führt der Dienst keine Änderungen aus. Ein
Authentik-Mitglied in `gitlab-users` oder `gitlab-admins` muss sich zunächst
einmal per OIDC anmelden, damit GitLab sein Konto erzeugt. Danach verwaltet der
Sync Aktivierung, ausstehende Bestätigung und den Adminstatus.

Die Token laufen nach einem Jahr ab. Vor Ablauf beide Token ersetzen und den
Dienst neu starten; die Secret-Inhalte nie in Shell-Historie, Logs oder Git
schreiben.

## Sicherheitsgrenze des Runners

Der Docker-Executor benötigt `/var/run/docker.sock`. Damit kann ein CI-Job mit
absichtlich missbräuchlichen Docker-Befehlen praktisch Host-Kontrolle erlangen.
Der Runner ist daher ausschließlich für eigene, vertrauenswürdige Projekte
vorgesehen, als geschützter Instance-Runner begrenzt. Niemals für fremde Forks,
öffentliche Beiträge oder unbekannte CI-Konfigurationen freigeben.

`privileged = false` bleibt gesetzt. Docker-in-Docker und Zugriff von
Build-Containern auf andere Anwendungsnetze gehören nicht zu diesem Profil.
Zusätzlich akzeptiert der Runner nur geschützte Refs mit dem Tag `docker`;
ungetaggte Jobs bleiben aus.

## Web IDE

Die GitLab Web IDE steht für Bearbeitung und Commit im Browser bereit. Für
ausführbare Entwicklungsumgebungen oder Kubernetes-Workspaces wäre später
zusätzliche Infrastruktur erforderlich; sie gehört nicht zum kompakten
Einzelserver-Profil.

Der unsichere Single-Origin-Fallback für Erweiterungen ist deaktiviert. Der
Browser muss für Web-IDE-Erweiterungen den vorgesehenen externen Extension-Host
erreichen können; andernfalls stehen Erweiterungen dort nicht zur Verfügung.

## Anwendungseinstellungen absichern

Selbstregistrierung und der Web-IDE-Single-Origin-Fallback sind GitLab-
Application-Settings in der Datenbank. Der Compose-One-Shot-Service
`gitlab-security-settings` setzt sie bei jedem `docker compose up`
reproduzierbar per interner API, beendet sich anschließend erfolgreich und
benötigt weder einen Port
noch eine Token-Ablage.

Falls die Werte nach einer gezielten Datenbankwiederherstellung sofort erneut
gesetzt werden sollen, kann dasselbe Verfahren manuell ausgelöst werden:

```bash
cd <PROJEKT_ROOT>/Compose/gitlab
./scripts/apply-security-settings.sh
```

Das Skript verwendet denselben lokalen Admin-API-Token ausschließlich zur
Laufzeit, gibt ihn nicht aus und kontrolliert anschließend beide Werte.
