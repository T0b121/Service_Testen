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

## 2. Interne und öffentliche Prüfungen

```bash
docker compose exec litellm \
  curl -fsS http://ollama:11434/api/tags
curl -I http://litellm.<DOMAIN>
```

Erwartet:

- die interne Abfrage enthält `qwen3:0.6b`,
- HTTP leitet mit `308` zu HTTPS weiter.

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
nur für Notfälle.

## 4. Virtual Key anlegen und API testen

Im LiteLLM-Dashboard einen Virtual Key nur für `qwen3:0.6b` erzeugen. Den Key
einmalig in einen Passwortmanager des Zielsystems übernehmen.

```bash
curl -fsS https://litellm.<DOMAIN>/v1/models \
  -H 'Authorization: Bearer <VIRTUAL_KEY>'

curl -fsS https://litellm.<DOMAIN>/v1/chat/completions \
  -H 'Authorization: Bearer <VIRTUAL_KEY>' \
  -H 'Content-Type: application/json' \
  -d '{"model":"qwen3:0.6b","messages":[{"role":"user","content":"Antworte ausschließlich mit OK."}]}'
```

Ohne Header muss derselbe Endpunkt mit `401` oder `403` abgewiesen werden.

Weiter mit [Betrieb und Clients](betrieb-und-clients.md).
