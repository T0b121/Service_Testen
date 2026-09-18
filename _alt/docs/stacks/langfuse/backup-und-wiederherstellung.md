# Langfuse-Stack: Backup und Wiederherstellung

Ein vollständiges Langfuse-Backup enthält die Volumes
`langfuse_postgresql_data`, `langfuse_clickhouse_data`,
`langfuse_clickhouse_logs` und `langfuse_valkey_data` sowie die lokale
`Compose/langfuse/.env`. Die `.env` enthält alle Datenbank-, OIDC-, S3- und
Projekt-Zugangswerte und wird getrennt, verschlüsselt und niemals im Git
archiviert.

Für eine konsistente Dateisicherung den Stack zuerst anhalten:

```bash
cd <PROJEKT_ROOT>/Compose/langfuse
docker compose stop
```

Danach Volumes gemäß der [globalen Backup-Anleitung](../../backup-und-wiederherstellung.md)
sichern und den Stack wieder starten. `docker compose down -v` darf nicht für
eine Sicherung verwendet werden, da es alle Langfuse-Daten zerstört.

Bei einer Wiederherstellung gehören Volumes und die dazu passende `.env`
immer zusammen. Danach die fünf Container-Healthchecks, OIDC-Login und einen
LiteLLM-Testtrace prüfen.
