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

Der Zugriff besteht aus zwei Schichten:

| Schicht | Verwaltung |
|---|---|
| Zugang zu `webui.<DOMAIN>` | Authentik-Gruppen `openwebui-users` oder `openwebui-admin` |
| Konto und Rolle in Open WebUI | Open WebUI → Admin Panel → Users |

Ein Benutzer braucht beide Berechtigungen. Entfernen aus einer Authentik-Gruppe
sperrt den äußeren Zugriff nach Ablauf der Sitzung; Deaktivieren eines lokalen
Kontos sperrt den Open-WebUI-Login.

## 4. Neustart und Update

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

Nach jedem Update Authentik-Schutz, lokalen Login und eine Modellanfrage
prüfen.

## 5. Spätere OIDC-Umstellung

Der vorbereitete Scope Mapping `Open WebUI Rollen` wird erst bei einer
eigenständigen Umstellung auf Open-WebUI-OIDC verwendet. Dann werden der
lokale Login und der Forward-Auth-Proxy bewusst durch eine native OIDC-
Konfiguration ersetzt; beide Verfahren nicht gleichzeitig mischen.

## 6. Regelmäßige Kontrollen

```bash
cd <PROJEKT_ROOT>/Compose/open-webui
docker compose ps
docker system df
df -h
```

Zusätzlich Größe und Backup von `openwebui_data`, Mitglieder der Authentik-
Gruppen, lokale Open-WebUI-Administratoren und das Produktionszertifikat
prüfen.
