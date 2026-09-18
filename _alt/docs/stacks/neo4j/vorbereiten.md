# Neo4j-Stack: Vorbereiten

`Compose/neo4j/.env` ist lokal und hat Modus `0600`:

```dotenv
DOMAIN=<DOMAIN>
NEO4J_VERSION=2026.07-community
```

Das native Docker Secret `secrets/neo4j_auth` enthält exakt
`neo4j/<PASSWORT>`. Das Image läuft als UID/GID `7474`, daher muss die Datei
nach ihrer Erstellung so geschützt werden:

```bash
sudo chown 7474:7474 secrets/neo4j_auth
sudo chmod 400 secrets/neo4j_auth
```

Die spätere Stack-Provisionierung muss diese Eigentümer- und Modusänderung
zwingend vor `docker compose up` durchführen. Das interne Netz entsteht einmalig:

```bash
docker network create --internal neo4j_clients
```
