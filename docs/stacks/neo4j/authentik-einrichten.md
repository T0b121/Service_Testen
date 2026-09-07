# Authentik für Neo4j

Produktiv eingerichtet:

```text
Gruppe: neo4j-users (Mitglied: akadmin)
Anwendung: Neo4j Access / neo4j-access
Launch URL: https://neo4j.<DOMAIN>/browser/
Provider: Neo4j Access Provider
Modus: Forward auth (single application)
External host: https://neo4j.<DOMAIN>/
Outpost: authentik Embedded Outpost
```

Die aktive Gruppenbindung zu `neo4j-users` ist nicht negiert, hat Reihenfolge
`0`, Timeout `30` und Fehlerergebnis `fail`. Die Callback-URIs liegen bewusst
an der Hostwurzel unter `/outpost.goauthentik.io/`, nicht unter `/browser/`.
