# LiteLLM-Stack: Erststart und Prüfung

Vorher müssen [Vorbereiten](vorbereiten.md) und
[Authentik einrichten](authentik-einrichten.md) abgeschlossen sein.

## 1. Starten

```bash
cd <PROJEKT_ROOT>/Compose/litellm
docker compose pull
docker compose up -d
docker compose ps
```

`litellm-postgresql` und `litellm` müssen `healthy` erreichen.
Beim ersten Start führt LiteLLM zahlreiche Datenbankmigrationen aus; das kann
einige Minuten dauern. Solange `litellm` noch `health: starting` zeigt, den
Fortschritt mit `docker compose logs --tail=200 litellm` prüfen.

## 2. Interne und öffentliche Prüfungen

```bash
docker compose exec litellm /app/.venv/bin/python -c \
  "from urllib.request import urlopen; print(urlopen('http://ollama:11434/api/tags').read().decode())"
curl -I http://litellm.<DOMAIN>
```

Erwartet:

- die interne Abfrage enthält `qwen3:0.6b`,
- HTTP leitet mit `308` zu HTTPS weiter,
- jeder Nicht-API-Pfad fordert vor der LiteLLM-Auslieferung eine
  Authentik-Anmeldung an.

## 3. Verwaltung anmelden

In einem privaten Browserfenster öffnen:

```text
https://litellm.<DOMAIN>/ui
```

1. **Sign in with SSO** wählen und mit einem Mitglied von `litellm-admin` bei
   Authentik anmelden.
2. Nach der Rückleitung erscheint das LiteLLM-Dashboard.
3. Den Master-Key nur für Verwaltungsaktionen verwenden.

Mitglieder der Authentik-Gruppe `litellm-admin` erhalten beim OIDC-Login
automatisch die Rolle `proxy_admin`. Der Zugang unter `/fallback/login` ist
nur für Fehler des LiteLLM-OIDC-Logins und bleibt hinter Authentik Forward
Auth.

## 4. Virtual Key anlegen und API testen

Im LiteLLM-Dashboard einen Virtual Key nur für `qwen3:0.6b` erzeugen:

```text
Owned By: You (nur für den Funktionstest)
Key Name: test-qwen3
Models: qwen3:0.6b
Key Type: AI APIs
```

Den Key einmalig in einen Passwortmanager übernehmen. Für ein produktives
Drittsystem einen eigenen Key mit `Service Account` als Eigentümer erstellen.

```bash
read -rsp 'Virtual Key: ' LITELLM_TEST_KEY; echo

curl -fsS https://litellm.<DOMAIN>/v1/models \
  -H "Authorization: Bearer ${LITELLM_TEST_KEY}"

curl -fsS https://litellm.<DOMAIN>/v1/chat/completions \
  -H "Authorization: Bearer ${LITELLM_TEST_KEY}" \
  -H 'Content-Type: application/json' \
  -d '{"model":"qwen3:0.6b","messages":[{"role":"user","content":"Antworte ausschließlich mit OK."}]}'

curl -sS -o /dev/null -w '%{http_code}\n' \
  https://litellm.<DOMAIN>/v1/models

unset LITELLM_TEST_KEY
```

Die erste Antwort enthält `qwen3:0.6b`, die zweite eine Modellantwort. Der
Aufruf ohne Header muss mit `401` oder `403` abgewiesen werden.

Weiter mit [Betrieb und Clients](betrieb-und-clients.md).
