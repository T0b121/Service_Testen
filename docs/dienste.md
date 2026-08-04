# Dienste

Diese Übersicht enthält nur die öffentlichen Adressen. Einrichtung, Betrieb und Fehlerbehebung stehen jeweils in der Dokumentation des zugehörigen Stacks.

| Dienst | Adresse | Zweck |
|---|---|---|
| Authentik | `https://auth.<DOMAIN>` | Anmeldung und Zugriffssteuerung |
| Traefik-Dashboard | `https://proxy.<DOMAIN>/dashboard/` | Proxy-Verwaltung |
| Part-DB | `https://partdb.<DOMAIN>` | Teileverwaltung |
| Ollama | `https://ollama.<DOMAIN>` | Durch Authentik geschützte Modell-API |
| Open WebUI | `https://webui.<DOMAIN>` | Browseroberfläche für Ollama hinter Authentik |
| LiteLLM | `https://litellm.<DOMAIN>/v1`<br>`https://litellm.<DOMAIN>/ui` | OpenAI-kompatible Modell-API per LiteLLM-Virtual-Key; Verwaltungsoberfläche hinter Authentik |

Für weitere öffentliche Dienste wird hier nur eine Zeile ergänzt. Die technische Beschreibung gehört in `docs/stacks/<stack>/`.
