# Neo4j-Stack: Übersicht

Neo4j Community ist die interne Graphdatenbank für spätere Anwendungen.

| Eigenschaft | Wert |
|---|---|
| Image | `neo4j:2026.07-community` (aktuell `2026.07.1`) |
| Web UI | `https://neo4j.<DOMAIN>/browser/` über Traefik und Authentik |
| Browser-Datenzugang | HTTPS über `neo4j.<DOMAIN>:443`; kein externer Bolt-Port |
| Bolt intern | `neo4j:7687` nur im Netzwerk `web` und `neo4j_clients` |
| HTTP intern | `http://neo4j:7474` |
| Persistenz | `neo4j_data`, `neo4j_logs` |
| Authentik | Gruppe `neo4j-users`, Forward Auth |

Neo4j Community unterstützt kein natives OIDC; dieses ist eine
Enterprise-Funktion. Authentik schützt daher den Browserzugriff, während der
native Neo4j-Administrator die Datenbank absichert. Es gibt keine Host-Ports.

Die Community Edition verwaltet genau eine Nutzdatenbank, standardmäßig
`neo4j`, zusätzlich zur internen Verwaltungsdatenbank `system`. Sie ist daher
für eigene Graph-Experimente vorgesehen und nicht als gemeinsamer, hart
getrennter Datenspeicher mehrerer Anwendungen. Braucht ein Dienst später
Neo4j mit eigener Datenisolation, erhält er eine eigene interne
Neo4j-Community-Instanz.
