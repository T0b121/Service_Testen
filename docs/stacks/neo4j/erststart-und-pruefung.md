# Neo4j-Stack: Erststart und Prüfung

```bash
cd <PROJEKT_ROOT>/Compose/neo4j
docker compose pull
docker compose up -d
docker compose ps
```

Erwartet wird `healthy` und ausschließlich `7473-7474/tcp, 7687/tcp`, niemals
eine Hostbindung. Die produktive Prüfung bestätigte:

- `cypher-shell` mit dem Secretkonto `neo4j` liefert `RETURN 1`.
- `https://neo4j.<DOMAIN>/` leitet ohne Sitzung zu Authentik weiter.
- Der Outpost-Ping liefert `204`.
- Kuma-Monitor **Neo4j** (ID `13`) prüft `http://neo4j:7474/` und liefert `200`.

Nach Authentik-Anmeldung `https://neo4j.<DOMAIN>/browser/` öffnen und sich mit
Benutzer `neo4j` sowie dem Passwortanteil der Secret-Datei anmelden. Im
Verbindungsdialog **Protocol** `https` wählen und als **Connection URL**
`neo4j.<DOMAIN>:443` eintragen. Dadurch laufen Browser-Abfragen über die
durch Traefik und Authentik geschützte Neo4j-HTTP-API; Bolt `7687` bleibt
Docker-intern.

Ein kompakter Funktionstest nach der Anmeldung:

```cypher
RETURN 1 AS ok;
```
