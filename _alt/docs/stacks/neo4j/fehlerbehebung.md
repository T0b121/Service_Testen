# Neo4j: Fehlerbehebung

Wenn Neo4j meldet, dass `/run/secrets/neo4j_auth` nicht lesbar ist, Eigentümer
und Modus exakt prüfen:

```bash
stat -c '%A %u:%g %n' Compose/neo4j/secrets/neo4j_auth
```

Erwartet: `-r-------- 7474:7474`. Das ist keine optionale Härtung, sondern
für die native Docker-Secret-Initialisierung erforderlich.

Bei fehlendem Browserzugriff Mitgliedschaft in `neo4j-users`, Provider im
Embedded Outpost und die Callback-URL an der Hostwurzel prüfen.
