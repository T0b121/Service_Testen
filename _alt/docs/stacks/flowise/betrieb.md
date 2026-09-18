# Flowise-Stack: Betrieb

## LiteLLM als Chat-Modell

In Flowise unter **Credentials** einen OpenAI-kompatiblen Zugang erstellen:

```text
Base path: http://litellm:4000/v1
API key: ein eigener LiteLLM Virtual Key
```

Nicht den LiteLLM-Master-Key verwenden. Der Virtual Key wird in der
LiteLLM-Verwaltungsoberfläche erzeugt und kann für Flowise gezielt begrenzt
und widerrufen werden. In einem Chatflow anschließend einen passenden
OpenAI-Chat-Model-Node mit diesem Credential auswählen.

## Qdrant als Vektorspeicher

Im Qdrant-Credential verwenden:

```text
URL: http://qdrant:6333
API key: <QDRANT_API_KEY>
```

Der Flowise-Container ist Mitglied von `qdrant_clients`. Die externe
Dashboard-Adresse darf nicht als Maschinenendpunkt verwendet werden.

## Neo4j als Graphdatenbank

Für einen Neo4j-Node verwenden:

```text
Connection URL: bolt://neo4j:7687
Benutzer: neo4j
Passwort: Passwortanteil hinter `neo4j/` aus Compose/neo4j/secrets/neo4j_auth
```

Das interne Netz ist vertrauenswürdig, daher wird kein externer HTTPS-/Bolt-S-
Endpunkt benötigt. `bolt://` verwendet absichtlich eine direkte Verbindung
ohne Routing auf die öffentliche Adresse. Für jede Anwendung eine eigene Neo4j-Datenbank und einen
eigenen Datenbankbenutzer anlegen; Flowise darf nicht unkontrolliert die
Standarddatenbank anderer Anwendungen verwenden.

## Aktualisierung

Vor einem Versionswechsel beide Volumes sichern. Danach Gesundheitscheck,
Authentik-Login und einen vorhandenen Chatflow testen:

```bash
cd <PROJEKT_ROOT>/Compose/flowise
docker compose pull
docker compose up -d
docker compose ps
```

Weiter mit [Backup und Wiederherstellung](backup-und-wiederherstellung.md).
