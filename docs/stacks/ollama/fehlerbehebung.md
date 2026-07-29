# Ollama-Stack: Fehlerbehebung

## 1. Standarddiagnose

```bash
cd <PROJEKT_ROOT>/Compose/ollama

docker compose config --quiet
docker compose ps -a
docker compose logs --tail=200 ollama
docker network inspect web
```

## 2. Image kann nicht geladen werden

Prüfen:

```bash
docker compose pull
curl -4 -I --connect-timeout 15 https://registry-1.docker.io/v2/
```

Ein HTTP-Status `401` von Docker Hub bedeutet, dass die Registry erreichbar
ist und eine Anmeldung verlangt. Bei Timeouts die Netcup-Ausgangsregeln für
HTTPS sowie DNS prüfen.

## 3. Container ist nicht healthy

```bash
docker compose ps
docker inspect ollama --format '{{json .State.Health}}'
docker compose logs --tail=200 ollama
```

Der Healthcheck führt `ollama list` aus. Fehler beim Start zuerst vor einem
Modell-Download beheben.

## 4. Modell nicht gefunden oder Download schlägt fehl

```bash
docker compose exec ollama ollama list
docker compose logs --tail=200 ollama
df -h
```

Den vollständigen Modellnamen einschließlich Tag verwenden. Genügend freien
Speicher und ausgehendes HTTPS müssen vorhanden sein.

## 5. Modellantwort ist langsam oder bricht ab

Der Basisstack nutzt CPU. Große Modelle können Arbeitsspeicher ausschöpfen
oder sehr langsam sein. Zuerst ein kleineres Modell verwenden und prüfen:

```bash
free -h
docker stats --no-stream ollama
```

Eine GPU-Konfiguration nicht als lokale Compose-Sonderänderung hinzufügen.

## 6. Externer Aufruf wird abgewiesen

Prüfen:

- DNS für `ollama.<DOMAIN>`,
- Traefik-Router und Outpost-Pfad,
- Mitgliedschaft in `ollama-users`,
- Binding der Anwendung `Ollama API`,
- Zuweisung zum Authentik Embedded Outpost.

```bash
curl -I https://ollama.<DOMAIN>/outpost.goauthentik.io/ping
```

Erwartet ist `204`.

Ein externer Ollama-CLI-Client kann keinen interaktiven Authentik-Login
durchführen. Das ist kein Grund, Traefik oder Authentik für die API zu
umgehen; siehe [Authentik einrichten](authentik-einrichten.md#6-wichtige-einschränkung-für-externe-clients).

## 7. TCP 11434 ist am Host erreichbar

Das ist nicht vorgesehen. Prüfen:

```bash
sudo ss -lntp | grep -E ':(11434)\s' || true
docker compose config
```

Die Compose-Datei darf nur `expose: 11434` enthalten, kein `ports:`-Mapping.
Den verursachenden Container oder Prozess prüfen; Ollama nicht mit einem
öffentlichen Host-Port nachrüsten.
