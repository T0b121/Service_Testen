# LiteLLM-Stack: Backup und Wiederherstellung

## Backup-Umfang

| Daten | Speicherort | Bewertung |
|---|---|---|
| Virtual Keys, Benutzer, Modelle und Verwaltungsdaten | Volume `litellm_postgresql_data` | erforderlich |
| Datenbankpasswort, Master-Key, Salt-Key, OIDC-Secret und Fallback-Passwort | lokale `.env` | erforderlich, verschlüsselt sichern |
| Authentik-Anwendung, OIDC-Provider und Gruppenbindung | Authentik-PostgreSQL-Backup des Core-Stacks | erforderlich |

Ohne den ursprünglichen `LITELLM_SALT_KEY` können verschlüsselte Werte aus der
LiteLLM-Datenbank nicht zuverlässig entschlüsselt werden.

## Wiederherstellung

1. Core-Stack und die Authentik-Konfiguration wiederherstellen.
2. Lokale `.env` mit unveränderten Geheimnissen im Modus `600` bereitstellen.
3. `litellm_postgresql_data` wiederherstellen.
4. LiteLLM starten und mit einem bestehenden Virtual Key `/v1/models` testen.
5. OIDC-Anmeldung bei Authentik und Zugriff auf `/ui` prüfen.
