# Uptime-Kuma-Stack: Erststart und Prüfung

## 1. Image laden und Stack starten

```bash
cd <PROJEKT_ROOT>/Compose/uptime-kuma
docker compose pull
docker compose up -d
docker compose ps
```

Nach der Startphase muss der Container `uptime-kuma` den Status `healthy`
anzeigen. Das offizielle Image enthält einen eigenen Healthcheck; beim ersten
Start kann dieser bis zu drei Minuten benötigen.

## 2. Logs prüfen

```bash
docker compose logs --tail=150 uptime-kuma
```

Es dürfen keine fortlaufenden Fehler oder Neustarts erscheinen.

## 3. Traefik, Authentik und TLS prüfen

Ohne Browser-Anmeldung muss HTTP auf HTTPS umleiten und HTTPS zu Authentik
weiterleiten:

```bash
curl -I http://uptime.<DOMAIN>
curl -I https://uptime.<DOMAIN>/
curl -I https://uptime.<DOMAIN>/outpost.goauthentik.io/ping
```

Erwartet:

- HTTP antwortet mit `301` oder `308` und einer HTTPS-Adresse.
- HTTPS antwortet ohne bestehende Sitzung mit `302` zur Authentik-Adresse.
- Der Outpost-Ping antwortet mit `204`.

Optional das ausgestellte Zertifikat prüfen:

```bash
openssl s_client \
  -connect uptime.<DOMAIN>:443 \
  -servername uptime.<DOMAIN> \
  </dev/null 2>/dev/null \
  | openssl x509 -noout -subject -issuer -dates
```

Der Subject muss `CN=uptime.<DOMAIN>` enthalten.

## 4. Embedded MariaDB auswählen

Beim ersten Start zeigt Kuma zunächst die Datenbankauswahl. Für diesen Stack
ist **Embedded MariaDB** verbindlich. Sie wird von Kuma im Volume
`uptime_kuma_data` betrieben und benötigt weder einen zusätzlichen
MariaDB-Container noch einen Port.

Die Compose-Variable `UPTIME_KUMA_ENABLE_EMBEDDED_MARIADB=1` stellt sicher,
dass diese Auswahl in der v2-Imagevariante verfügbar ist.

Nach der Auswahl initialisiert Kuma seine Datenbank selbst. In den Logs muss
anschließend Folgendes erscheinen:

```text
Database Type: embedded-mariadb
Embedded MariaDB is ready for connections
No user, need setup
```

## 5. Lokalen Uptime-Kuma-Administrator anlegen

1. `https://uptime.<DOMAIN>/` im Browser öffnen.
2. Bei Authentik anmelden. Der Benutzer muss Mitglied von
   `uptime-kuma-users` sein.
3. Danach in Uptime Kuma den lokalen Notfalladministrator `kuma-admin`
   anlegen oder den bereits angelegten Zugang verwenden.
4. Das Passwort ausschließlich aus
   `Compose/uptime-kuma/secrets/uptime_kuma_admin_password` in einen
   Passwortmanager übernehmen; die Datei hat Berechtigung `0600`.
5. Unter **Settings → Security** Zwei-Faktor-Authentifizierung aktivieren.

Der lokale Uptime-Kuma-Administrator ersetzt Authentik nicht: Authentik
steuert, wer die Oberfläche überhaupt erreichen darf; Uptime Kuma steuert die
eigentliche Überwachungskonfiguration.

## 6. Eingerichtete Monitore prüfen

Uptime Kuma hat keinen Docker-Socket und überwacht deshalb Dienste über ihre
Netzwerkerreichbarkeit. Die Instanz enthält diese internen HTTP-Monitore mit
60 Sekunden Intervall:

| Name | URL | Sollstatus |
|---|---|---|---|
| Traefik | `http://core-traefik:8082/ping` | `200` |
| Authentik | `http://core-authentik-server:9000/-/health/live/` | `200` |
| Ollama | `http://ollama:11434/` | `200` |
| Open WebUI | `http://open-webui:8080/health` | `200` |
| LiteLLM | `http://litellm:4000/health/liveliness` | `200` |
| SearXNG | `http://searxng:8080/` | `200` |
| Jellyfin | `http://jellyfin:8096/health` | `200` |
| Part-DB | `http://partdb-server/` mit Proxy-Headern | `200` bis `399` |
| Nextcloud | `http://nextcloud/status.php` | `200` |
| ONLYOFFICE | `http://nextcloud-onlyoffice/healthcheck` | `200` |
| GitLab | `http://gitlab/users/sign_in` mit Proxy-Headern | `200` |

Part-DB erwartet den öffentlichen Hostnamen und wird daher intern mit
`Host`, `X-Forwarded-Host` und `X-Forwarded-Proto: https` abgefragt. Die
reguläre Weiterleitung auf die Sprachroute ist dort zulässig.

GitLab verwendet intern ebenfalls die Header `Host: gitlab.<DOMAIN>` und
`X-Forwarded-Proto: https`. Der Pfad `/-/health` ist über den internen
Webserver nicht verfügbar und liefert `404`; deshalb überwacht Kuma stattdessen
die öffentliche Anmeldeseite über die interne Docker-Adresse.

Alle anderen Monitore prüfen ausschließlich interne Ziele im Docker-Netzwerk
`web`; weder externe Domains noch ungeschützte Browserendpunkte werden dafür
verwendet.

### Vormerkungen für die geplanten Stacks

Die folgenden acht HTTP-Monitore wurden auf Wunsch bereits angelegt. Sie sind
bis zur jeweiligen Bereitstellung absichtlich rot. Die Zielnamen folgen den
vorgesehenen Compose-Servicenamen und werden beim Einrichten des jeweiligen
Stacks gegen dessen echten internen Health-Endpunkt geprüft und nötigenfalls
aktualisiert:

```text
Qdrant, Neo4j, Langfuse, Flowise, n8n, Paperless-ngx, LocalAI und ComfyUI
```

Der jeweilige Stack-Commit dokumentiert Name, Monitor-Typ, interne Adresse,
Sollstatus und den ersten erfolgreichen Heartbeat. Die spätere zentrale
Einrichtungs-CLI wird dagegen keine roten Vormerkungen erzeugen: Dort wird ein
Monitor erst nach dem erfolgreichen internen Healthcheck erstellt.

## 7. Funktionstest

Einen Monitor bewusst anhalten oder eine ungültige Test-URL anlegen. Nach dem
festgelegten Prüfintervall muss Uptime Kuma den Status als fehlerhaft anzeigen.
Danach das Ziel wiederherstellen beziehungsweise den Testmonitor löschen und
prüfen, dass der Status erneut `Up` wird.

Weiter mit [Betrieb](betrieb.md).
