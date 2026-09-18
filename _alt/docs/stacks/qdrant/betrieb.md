# Qdrant-Stack: Betrieb

## Interne Clients

Ein späterer Dienst, der Qdrant benötigt, tritt dem externen Docker-Netz
`qdrant_clients` bei und verwendet:

```text
REST: http://qdrant:6333
gRPC: qdrant:6334
Header: api-key: <QDRANT_API_KEY>
```

Der Schlüssel wird dem jeweiligen Dienst lokal über dessen ignorierte `.env`
oder über dessen unterstützten Secret-Mechanismus gegeben. Er gehört nie in
eine versionierte Compose-Datei.

## Dashboard

Das Dashboard kann Collections erstellen, Punkte ändern und Snapshots
hochladen. Authentik entscheidet, wer die Seite erreicht; der API-Schlüssel
entscheidet, ob Qdrant die Aktion akzeptiert. Beide Schutzschichten bleiben
aktiv.

## Aktualisierung

Vor einem Pull Snapshot und Volume-Sicherung durchführen. Der Tag `v1.19`
übernimmt Patch-Releases innerhalb dieser Linie, aber kein Update auf `v1.20`.

```bash
cd <PROJEKT_ROOT>/Compose/qdrant
docker compose pull
docker compose up -d
docker compose ps
```

Danach Schlüsseltest und Kuma-Heartbeat gemäß
[Erststart und Prüfung](erststart-und-pruefung.md) wiederholen.
