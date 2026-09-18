# Flowise-Stack: Backup und Wiederherstellung

Flowise benötigt beide persistenten Bereiche:

| Speicher | Inhalt |
|---|---|
| `flowise_postgresql_data` | Benutzer, Chatflows, Credentials-Metadaten und Einstellungen |
| `flowise_data` | Verschlüsselte Credential-Dateien, Speicherobjekte und Logs |

Vor einem Backup den Stack anhalten oder einen konsistenten PostgreSQL-Dump
erstellen. `FLOWISE_SECRETKEY_OVERWRITE` aus der lokalen `.env` muss gemeinsam
mit dem Backup gesichert werden. Ohne genau diesen Schlüssel können bereits
gespeicherte Credentials nach einer Wiederherstellung nicht entschlüsselt
werden.

Wiederherstellung:

1. Stack stoppen.
2. Beide Volumes und die lokale `.env` aus demselben Sicherungsstand
   wiederherstellen.
3. Eigentümer des externen `flowise_data` bei Bedarf erneut auf `1000:1000`
   setzen.
4. Stack starten.
5. Healthcheck, Authentik-Login und einen Chatflow prüfen.

LiteLLM-, Qdrant- und Neo4j-Zugangsdaten liegen zusätzlich in ihren eigenen
Stacks und werden dort separat gesichert beziehungsweise neu erstellt.
