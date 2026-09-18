# Open-WebUI-Stack: Betrieb

## 1. Status und Logs

```bash
cd <PROJEKT_ROOT>/Compose/open-webui

docker compose ps
docker compose logs --tail=200 open-webui
```

## 2. Modellnutzung

Open WebUI erhält die Modellauswahl direkt von Ollama über:

```text
http://ollama:11434
```

Modelle werden im Ollama-Stack verwaltet:

```bash
cd <PROJEKT_ROOT>/Compose/ollama
docker compose exec ollama ollama list
```

Nach dem Herunterladen eines weiteren Modells die Open-WebUI-Seite neu laden
oder die Modellliste dort aktualisieren.

## 3. Zugang verwalten

Der Zugriff wird zentral in Authentik verwaltet:

| Aufgabe | Verwaltung |
|---|---|
| Zugang und Rolle `user` | Authentik-Gruppe `openwebui-users` |
| Rolle `admin` | Authentik-Gruppe `openwebui-admin` |

Open WebUI übernimmt die Rolle beim OIDC-Login aus dem Authentik-Claim
`roles`. Nach Gruppenänderungen muss sich der Benutzer ab- und wieder anmelden.

## 4. Online-Suche mit SearXNG

Netzwerk, globale Suchmaschine, Modellprofil, Werkzeugauswahl und Chat-Test
stehen vollständig in [Websuche mit SearXNG](websuche-mit-searxng.md).
Die öffentliche SearXNG-Adresse ersetzt nicht die interne Query URL
`http://searxng-internal:8080/search?q=<query>`.

## 5. Neustart und Update

```bash
cd <PROJEKT_ROOT>/Compose/open-webui
docker compose up -d
```

Vor einem Update Release Notes prüfen und `OPEN_WEBUI_VERSION` in `.env`
bewusst ändern. Danach:

```bash
docker compose pull
docker compose up -d
docker compose ps
```

Nach jedem Update OIDC-Anmeldung, Rollen und eine Modellanfrage prüfen.

## 6. Regelmäßige Kontrollen

```bash
cd <PROJEKT_ROOT>/Compose/open-webui
docker compose ps
docker system df
df -h
```

Zusätzlich Größe und Backup von `openwebui_data`, Mitglieder der Authentik-
Gruppen, OIDC-Provider und -Scope-Mapping sowie das Produktionszertifikat
prüfen.
