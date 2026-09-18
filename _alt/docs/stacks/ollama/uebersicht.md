# Ollama-Stack: Übersicht

Der Stack stellt Ollama als lokalen Modellserver bereit. Die öffentliche API
läuft ausschließlich über Traefik und Authentik unter
`https://ollama.<DOMAIN>`.

## Dienste

| Dienst | Zweck | Erreichbarkeit |
|---|---|---|
| `ollama` | Modellverwaltung und Ollama-API | intern: `http://ollama:11434`; extern: `https://ollama.<DOMAIN>` über Traefik und Authentik |

## Architektur

```text
Internet
  -> Traefik :443
  -> Authentik Forward Auth
  -> Ollama :11434

Weitere vertrauenswürdige Container im Netzwerk web
  -> http://ollama:11434
```

Ollama besitzt kein Host-Portmapping. TCP 11434 ist weder direkt am Server noch
in der Netcup-Firewall freizugeben.

Der gemeinsame Zugriff im Docker-Netzwerk `web` ist bewusst vorgesehen. Der
Open-WebUI-Stack und eine gezielt erweiterte Part-DB-Integration können Ollama
über `http://ollama:11434` direkt ansprechen. Diese interne Verbindung
umgeht Traefik und Authentik; nur vertrauenswürdige Dienste werden deshalb mit
`web` verbunden.

## Voraussetzungen

- Core-Stack läuft mit Traefik und Authentik.
- Das externe Docker-Netzwerk `web` existiert.
- DNS für `ollama.<DOMAIN>` zeigt auf den Server.
- TCP 80 und 443 sind extern erreichbar.
- Die Authentik-Gruppe `ollama-users` ist für die externe API vorgesehen.

## Persistente Daten

| Volume | Inhalt |
|---|---|
| `ollama_data` | heruntergeladene Modelle, Modellmanifest und lokale Ollama-Daten |

Modelle können mehrere Gigabyte groß sein. Das Volume nicht entfernen, solange
die Modelle weiter benötigt werden.

## Kein GPU-Support im Basissystem

Dieser Stack nutzt absichtlich CPU. NVIDIA-, AMD- oder andere GPU-Runtimes
werden nicht implizit installiert oder an Container durchgereicht. Eine spätere
GPU-Erweiterung ist eine separate, versionierte Stackänderung.

Weiter mit:

- [Vorbereiten](vorbereiten.md)
- [Authentik einrichten](authentik-einrichten.md)
- [Erststart und Prüfung](erststart-und-pruefung.md)
- [Externe Python-API](externe-python-api.md)
- [Betrieb](betrieb.md)
