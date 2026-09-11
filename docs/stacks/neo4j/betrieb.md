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

## Optionaler MCP-Server

Der interne Dienst `neo4j-mcp` stellt die Neo4j-MCP-Tools `get-schema`,
`read-cypher`, `write-cypher` und `list-gds-procedures` bereit. Er hat keinen
Host-Port und gehört ausschließlich zum internen Netzwerk `neo4j_clients`.
APOC ist aktiviert, weil die Schema-Ermittlung des offiziellen MCP-Servers es
benötigt.

Die Einbindung geschieht absichtlich nicht automatisch über Compose oder eine
LiteLLM-Konfigurationsdatei. Wer Neo4j nicht verwendet, erhält dadurch weder
ein unnötiges Netzwerkmitglied noch einen Datenbankzugriff. Die optionale
manuelle LiteLLM-Konfiguration steht unter
[LiteLLM: Betrieb und Clients](../litellm/betrieb-und-clients.md).

`X-Neo4j-MCP-ReadOnly: false` erlaubt Schreiboperationen. Ein n8n-Agent darf
diesen MCP-Server daher nur über einen eigenen LiteLLM-Virtual-Key erhalten,
der ausdrücklich für ihn bestimmt ist. Der Agent-Prompt muss Schreibvorgänge
auf explizite Nutzeranweisungen begrenzen und darf keine Lösch-Tools anbieten.

Die spätere `Compose/neo4j/provision.py` übernimmt mindestens die generischen
zentralen Parameter sowie `--neo4j-auth-file`; sie erstellt das Secret,
setzt Besitzer `7474:7474` und Modus `0400` idempotent.
