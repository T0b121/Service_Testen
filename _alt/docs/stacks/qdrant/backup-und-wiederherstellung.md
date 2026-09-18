# Qdrant-Stack: Backup und Wiederherstellung

Qdrant-Daten liegen dauerhaft im Volume `qdrant_storage`. Für konsistente
logische Sicherungen pro Collection zusätzlich Qdrant-Snapshots erzeugen. Die
REST-API dafür verlangt den Admin-API-Schlüssel:

```text
POST /collections/<COLLECTION>/snapshots
Header: api-key: <QDRANT_API_KEY>
```

Snapshots liegen im persistenten Storage unter `/qdrant/storage/snapshots`.
Sichere das gesamte Volume im regulären Docker-Volume-Backup, nicht nur
einzelne Snapshots.

Bei einer Wiederherstellung:

1. Stack stoppen.
2. Gesichertes Volume wiederherstellen oder eine leere Collection anlegen.
3. Snapshot über das geschützte Dashboard oder die interne Qdrant-API
   wiederherstellen.
4. Stack starten und mit Schlüsseltest sowie Kuma-Heartbeat prüfen.

Der API-Schlüssel ist nicht Teil des Volumes. Die lokale `.env` muss aus dem
verschlüsselten Konfigurationsbackup separat wiederhergestellt werden.
