# Neo4j-Stack: Betrieb

Interne Clients treten `neo4j_clients` bei und nutzen `bolt://neo4j:7687` mit
dem nativen Neo4j-Konto. Die öffentliche Browseradresse ist kein
Maschinenendpunkt. Der integrierte Neo4j Browser nutzt dagegen ausdrücklich
`https://neo4j.<DOMAIN>:443`; diese HTTP-API-Route ist durch Authentik
geschützt und erfordert zusätzlich die native Neo4j-Anmeldung.

Testgraphen lassen sich vollständig leeren, ohne die Datenbank selbst oder
ihre Konfiguration zu ersetzen:

```cypher
MATCH (n)
DETACH DELETE n;
```

Anschließend muss `MATCH (n) RETURN count(n);` den Wert `0` liefern. Anzeigen
für Labels oder Property Keys im Neo4j Browser können bis zum Neuladen der
Seite zwischengespeichert bleiben; sie belegen keine verbliebenen Daten.

Neo4j 2026.07 protokolliert standardmäßig Hinweise zu akzeptierten
X-Forwarded-Headern. Der Stack veröffentlicht trotzdem keinen Datenbankport;
Traefik und Authentik bleiben die einzige Browserroute. Eine unbestätigte
Neo4j-Konfigurationsoption darf diese Warnung nicht unterdrücken.

Die spätere `Compose/neo4j/provision.py` übernimmt mindestens die generischen
zentralen Parameter sowie `--neo4j-auth-file`; sie erstellt das Secret,
setzt Besitzer `7474:7474` und Modus `0400` idempotent.
