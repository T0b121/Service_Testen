# GitLab-Stack: Übersicht

Der Stack besteht aus GitLab CE, einem einzelnen Docker-Runner und dem lokalen
`gitlab-auth-sync`-Dienst. Authentik bleibt die Berechtigungsquelle: Die
Gruppen `gitlab-users` und `gitlab-admins` steuern aktive GitLab-OIDC-Konten
beziehungsweise globale GitLab-Administratoren. Der Sync fragt Authentik alle
fünf Minuten per API ab und nutzt keine zusätzlichen externen Dienste oder
offenen Host-Ports.

Der Stack betreibt GitLab Community Edition und einen einzelnen GitLab Runner
für private Projekte eines einzelnen Betreibers. GitLab bündelt PostgreSQL,
Redis, Gitaly und den Webdienst im offiziellen Omnibus-Container. Der Runner
erstellt für jeden CI-Job einen separaten Docker-Container.

| Komponente | Aufgabe | Erreichbarkeit |
|---|---|---|
| GitLab CE | Repositories, Issues, Merge Requests und Web IDE | `https://gitlab.<DOMAIN>` über Traefik |
| GitLab über HTTPS | Klonen und Pushen per HTTPS | `https://gitlab.<DOMAIN>` |
| GitLab Runner | ein paralleler Docker-CI-Job | nur intern |

GitLab verwendet Authentik nativ per OIDC und ausschließlich HTTPS für Git.
Der vorhandene Host-SSH-Port 22 bleibt allein dem Server vorbehalten. Es gibt
keinen weiteren geöffneten GitLab-Port. Es gibt bewusst kein Traefik
Forward Auth vor GitLab: Die Anmeldung einschließlich der OIDC-Rückrufroute
bleibt bei GitLab selbst.

Das Profil ist für den Einzelbetrieb auf diesem Host ausgelegt: maximal 8 GiB
für GitLab, ein Runner und genau ein paralleler CI-Job. Container Registry,
Pages, Kubernetes Agent, Mattermost und das interne Prometheus-Monitoring sind
deaktiviert. Uptime Kuma übernimmt die externe Verfügbarkeitsüberwachung.

Weiter mit [Vorbereiten](vorbereiten.md).
