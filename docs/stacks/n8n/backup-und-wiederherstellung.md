# n8n-Stack: Backup und Wiederherstellung

n8n benötigt beide persistenten Bereiche:

| Speicher | Inhalt |
|---|---|
| `n8n_postgresql_data` | Workflows, Ausführungen, Benutzer, Credentials-Metadaten und Einstellungen |
| `n8n_data` | lokale n8n-Dateien und Anwendungszustand |

Zusätzlich müssen aus der lokalen `.env` gesichert werden:

- `N8N_ENCRYPTION_KEY` — ohne diesen Schlüssel sind gespeicherte Credentials
  nicht mehr entschlüsselbar.
- `N8N_RUNNERS_AUTH_TOKEN` — muss zum wiederhergestellten Stack passen.
- die PostgreSQL-Zugangsdaten.

Wiederherstellung:

1. Stack anhalten.
2. PostgreSQL-Volume und `n8n_data` aus demselben Sicherungsstand
   wiederherstellen.
3. Die passende lokale `.env` zurücklegen.
4. Stack starten.
5. Healthcheck, Authentik-Login, einen Code-Node und einen repräsentativen
   Workflow testen.

LiteLLM-Virtual-Keys und MCP-Server liegen außerhalb von n8n und werden im
LiteLLM-Stack separat gesichert beziehungsweise erneut konfiguriert.
