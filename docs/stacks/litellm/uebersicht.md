# LiteLLM-Stack: Übersicht

LiteLLM stellt einen lokal betriebenen, OpenAI-kompatiblen API-Gateway vor
Ollama bereit. Die öffentliche API lautet `https://litellm.<DOMAIN>/v1`; die
Verwaltungsoberfläche ist unter `https://litellm.<DOMAIN>/ui` erreichbar.

## Architektur und Zugriff

```text
Maschinenclient
  -> HTTPS /v1 mit LiteLLM-Virtual-Key
  -> Traefik
  -> LiteLLM :4000
  -> Ollama :11434

Administrator
  -> HTTPS /ui
  -> LiteLLM OIDC
  -> Authentik
  -> LiteLLM :4000
```

Die API wird bewusst nicht über Authentik-OIDC geschützt: ein
Maschinenclient kann keinen interaktiven Browser-Login durchführen. LiteLLM
validiert stattdessen jeden API-Aufruf mit einem eigenen Virtual Key. Ohne
gültigen `Authorization: Bearer`-Header werden weder Modelle noch Antworten
bereitgestellt.

Der LiteLLM-Master-Key ist ausschließlich für die Verwaltung bestimmt und
wird nie an Clients verteilt. Für jedes externe System wird ein eigener,
widerrufbarer Virtual Key mit passender Modellfreigabe ausgestellt.

LiteLLM verwendet für `/ui` natives OIDC mit Authentik. Laut LiteLLM ist dieses
Admin-UI-SSO seit Version 1.76.0 bis zu fünf Nutzer kostenlos. Der lokale
Fallback-Login bleibt ausschließlich für Wiederherstellungsfälle verfügbar.

## Dienste und Daten

| Dienst | Aufgabe | Netzwerk |
|---|---|---|
| `litellm` | API-Proxy, Key- und Modellverwaltung | `web`, `litellm_internal` |
| `litellm-postgresql` | persistente LiteLLM-Daten | nur `litellm_internal` |
| `ollama` | lokale Modell-API | `web` |

Das Volume `litellm_postgresql_data` enthält Virtual Keys, Benutzer, Modelle
und Verwaltungsdaten. `LITELLM_MASTER_KEY` und `LITELLM_SALT_KEY` müssen
unverändert erhalten bleiben; ein Wechsel kann den Zugriff auf verschlüsselte
Einträge in der Datenbank verhindern.

Weiter mit:

- [Vorbereiten](vorbereiten.md)
- [Authentik einrichten](authentik-einrichten.md)
- [Erststart und Prüfung](erststart-und-pruefung.md)
