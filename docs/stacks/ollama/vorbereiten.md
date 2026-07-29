# Ollama-Stack: Vorbereiten

Vorher abschließen:

- [Server konfigurieren](../../server/konfigurieren.md)
- [Core-Stack: Erststart und Prüfung](../core/erststart-und-pruefung.md)

## 1. Versionierte Dateien prüfen

```bash
cd <PROJEKT_ROOT>

find Compose/ollama -maxdepth 2 -type f -print | sort
```

Erwartet:

```text
Compose/ollama/compose.yml
```

## 2. `.env` erstellen

```bash
cd <PROJEKT_ROOT>/Compose/ollama
nano .env
```

Inhalt:

```dotenv
# Domain
DOMAIN=<DOMAIN>

# Docker Image Version
# Bewusst kein latest-Tag verwenden.
OLLAMA_VERSION=0.32.5

# Ollama
# Wie lange ein verwendetes Modell nach einer Anfrage im Arbeitsspeicher bleibt.
OLLAMA_KEEP_ALIVE=5m
```

`OLLAMA_VERSION` bezeichnet eine bewusst gewählte Ollama-Version und wird erst
bei einem geplanten Update geändert. Kein `latest` verwenden.

Dateirechte und Git-Schutz prüfen:

```bash
chmod 600 .env
stat -c '%A %n' .env
git check-ignore -v .env
```

Erwartet: `-rw-------` und eine passende `.gitignore`-Regel.

## 3. DNS prüfen

```bash
cd <PROJEKT_ROOT>

getent ahostsv4 ollama.<DOMAIN>
getent ahostsv6 ollama.<DOMAIN>
```

Die Ergebnisse müssen auf die öffentlichen Serveradressen zeigen. Bei
bewusst nicht verwendetem IPv6 darf die IPv6-Abfrage ohne Ausgabe bleiben.

## 4. Netzwerk prüfen

```bash
docker network inspect web \
  --format 'Name={{.Name}} Driver={{.Driver}} Scope={{.Scope}}'
```

Erwartet:

```text
Name=web Driver=bridge Scope=local
```

## 5. Konfiguration prüfen

```bash
cd <PROJEKT_ROOT>/Compose/ollama
docker compose config --quiet
```

Erwartet: keine Ausgabe und Exit-Code `0`.

Es darf kein `ports:`-Mapping für 11434 geben. `expose: 11434` ist dagegen
erwartet und veröffentlicht keinen Port am Host.

## 6. Keine manuell anzulegenden Secret-Dateien erforderlich

Der Ollama-Basisstack benötigt keine manuell anzulegenden Passwörter,
API-Schlüssel oder Secret-Dateien unter `Compose/ollama/secrets/`. Die externe
Zugriffskontrolle liegt bei Authentik.

Beim ersten Start erzeugt Ollama einen eigenen privaten Dienstschlüssel im
Volume `ollama_data`. Dieser wird weder manuell erstellt noch aus dem Volume
ausgelesen. Ein Backup dieses Volumes ist wie jedes Secret-haltige Backup zu
verschlüsseln und gehört nicht in Git.

Weiter mit [Authentik einrichten](authentik-einrichten.md).
