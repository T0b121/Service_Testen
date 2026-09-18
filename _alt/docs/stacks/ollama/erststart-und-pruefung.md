# Ollama-Stack: Erststart und Prüfung

Vorher müssen [Vorbereiten](vorbereiten.md) und [Authentik einrichten](authentik-einrichten.md) abgeschlossen sein.

## 1. Image laden und starten

```bash
cd <PROJEKT_ROOT>/Compose/ollama

docker compose pull
docker compose up -d
```

## 2. Status prüfen

```bash
docker compose ps
```

Erwartet:

```text
ollama   healthy
```

## 3. API intern prüfen

```bash
docker compose exec ollama ollama list
```

Beim ersten Start ist eine leere Modelltabelle erwartbar. Die erfolgreiche
Ausführung bestätigt, dass der Dienst erreichbar ist.

Zusätzlich:

```bash
docker compose exec ollama \
  ollama ps
```

Ohne laufende Modellanfrage ist eine leere Tabelle erwartbar.

## 4. Öffentlichen Zugang und Authentik prüfen

```bash
curl -I http://ollama.<DOMAIN>
curl -I https://ollama.<DOMAIN>
curl -I https://ollama.<DOMAIN>/outpost.goauthentik.io/ping
```

Erwartet:

- HTTP liefert einen `308`-Redirect zu HTTPS.
- HTTPS liefert ohne vorhandene Authentik-Sitzung eine Weiterleitung zur
  Authentik-Anmeldung, keinen direkten Ollama-Inhalt.
- Der Outpost-Ping liefert `204`.

Danach in einem privaten Browserfenster `https://ollama.<DOMAIN>` öffnen:

- Benutzer in `ollama-users` darf sich bei Authentik anmelden und erreicht die
  Ollama-API. Im Browser erscheint am Wurzelpfad `Ollama is running`.
- Ein Benutzer ohne diese Gruppe wird durch Authentik abgewiesen.

Die `Location`- und `Set-Cookie`-Header einer Authentik-Weiterleitung können
kurzlebige Sitzungsdaten enthalten. Diese Werte nicht in Tickets, Chats oder
andere öffentliche Ausgaben kopieren.

## 5. Modell bewusst laden

Ein Modell erst laden, wenn genügend Speicherplatz und Arbeitsspeicher für
dessen Größe vorhanden sind. Für einen kompakten Funktionstest wurde
`qwen3:0.6b` verwendet:

```bash
docker compose exec ollama ollama pull qwen3:0.6b
docker compose exec ollama ollama list
```

Eine einfache lokale Modellanfrage danach:

```bash
docker compose exec ollama \
  ollama run qwen3:0.6b 'Antworte ausschließlich mit OK.'
```

Je nach Modell kann vor der Antwort eine Denkpassage erscheinen. Entscheidend
ist, dass am Ende die erwartete Antwort ohne Fehlermeldung ausgegeben wird.
Keine großen Modelle nur als Healthcheck laden.

## 6. Abschließende Prüfung

```bash
docker compose logs --since=15m ollama
docker network inspect web
sudo ss -lntp | grep -E ':(11434)\s' || true
```

Erwartet:

- Ollama bleibt `healthy`.
- `ollama` ist im Netzwerk `web`.
- Es gibt kein Host-Portmapping für TCP 11434.
- keine wiederkehrenden Start- oder Modellfehler.

Weiter mit [Betrieb](betrieb.md).
