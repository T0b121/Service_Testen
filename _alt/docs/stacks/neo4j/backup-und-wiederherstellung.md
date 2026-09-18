# Neo4j: Backup und Wiederherstellung

Community Edition unterstützt konsistente Offline-Dumps. Vor einem Dump den
Stack stoppen, anschließend `neo4j-admin database dump neo4j` verwenden und
`neo4j_data` sowie die Secretdatei getrennt und verschlüsselt sichern. Online
Backups sind eine Enterprise-Funktion.

Zum Wiederherstellen Stack stoppen, einen Dump mit `neo4j-admin database load`
in ein leeres Datenvolume laden, dann starten und Bolt, Browserweg und Kuma
prüfen.
