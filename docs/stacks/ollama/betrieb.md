# Ollama-Stack: Betrieb

## 1. Status und Logs

```bash
cd <PROJEKT_ROOT>/Compose/ollama

docker compose ps
docker compose logs --tail=200 ollama
```

## 2. Modelle verwalten

Installierte Modelle anzeigen:

```bash
docker compose exec ollama ollama list
```

Ein Modell herunterladen:

```bash
docker compose exec ollama ollama pull <MODELL>:<TAG>
```

Ein Modell entfernen:

```bash
docker compose exec ollama ollama rm <MODELL>:<TAG>
```

Vor dem Download die Modellgröße, den freien Speicherplatz und den
Arbeitsspeicher prüfen. Ein Download verändert das persistente Volume
`ollama_data`.

## 3. Interne Nutzung durch weitere Stacks

Ein weiterer vertrauenswürdiger Stack verbindet seinen benötigten Dienst mit
dem externen Docker-Netzwerk `web` und verwendet als Ollama-Basisadresse:

```text
http://ollama:11434
```

Diese Adresse ist ausschließlich für Container im Netzwerk `web`. Sie wird
nicht in Browsern oder auf dem Host verwendet und umgeht bewusst die äußere
Authentik-Prüfung.

## 4. Externe Nutzung

Die externe Adresse lautet:

```text
https://ollama.<DOMAIN>
```

Sie bleibt durch Authentik geschützt. Für Browserzugriff ist eine Sitzung eines
Benutzers aus `ollama-users` erforderlich. Die Einschränkung für automatisierte
Ollama-Clients steht unter [Authentik einrichten](authentik-einrichten.md#6-wichtige-einschränkung-für-externe-clients).

## 5. Neustart und Update

Normal neu starten:

```bash
docker compose up -d
```

Vor einem Update:

1. Modellliste dokumentieren.
2. Sicherung oder Wiederherstellungsplan prüfen.
3. Release Notes der gewählten Ollama-Version prüfen.
4. `OLLAMA_VERSION` in der lokalen `.env` bewusst ändern.

Danach:

```bash
docker compose pull
docker compose up -d
docker compose ps
docker compose exec ollama ollama list
```

## 6. Regelmäßige Kontrollen

```bash
docker compose ps
docker system df
df -h
```

Zusätzlich regelmäßig prüfen:

- Größe von `ollama_data`,
- nicht mehr benötigte Modelle,
- Mitglieder der Authentik-Gruppe `ollama-users`,
- Produktionszertifikat von `ollama.<DOMAIN>`,
- erfolgreiche Authentik-Anmeldung für die vorgesehenen Benutzer.
