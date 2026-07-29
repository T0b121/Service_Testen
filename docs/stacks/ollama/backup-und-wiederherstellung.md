# Ollama-Stack: Backup und Wiederherstellung

## 1. Backup-Umfang

| Daten | Speicherort | Bewertung |
|---|---|---|
| Ollama-Modelle, Manifeste und Dienstschlüssel | Volume `ollama_data` | optional; Modelle können erneut geladen werden, ein Volume-Backup verschlüsseln |
| Version und Modellliste | lokale Dokumentation oder Backup-Manifest | empfohlen |
| Zugriffsgruppen und Provider | Authentik-PostgreSQL-Backup des Core-Stacks | erforderlich für die äußere Zugriffskontrolle |

Für Testmodelle genügt meist die dokumentierte Modellliste. Ein vollständiges
Volume-Backup kann sehr groß werden und enthält den von Ollama beim ersten
Start erzeugten privaten Dienstschlüssel. Es wird verschlüsselt gesichert und
nicht in Git abgelegt.

## 2. Modellliste sichern

```bash
cd <PROJEKT_ROOT>/Compose/ollama
docker compose exec ollama ollama list
```

Die Ausgabe nicht blind in Git ablegen; sie kann in einem verschlüsselten
Backup-Manifest gespeichert werden.

## 3. Volume sichern

Vor einer konsistenten Sicherung den Stack anhalten:

```bash
cd <PROJEKT_ROOT>/Compose/ollama
docker compose stop ollama
```

Die Sicherung erfolgt außerhalb des Repositorys nach der projektweiten
[Backup-Strategie](../../backup-und-wiederherstellung.md). Danach wieder
starten:

```bash
docker compose up -d
```

## 4. Wiederherstellung

Reihenfolge:

1. Core-Stack und Authentik wiederherstellen, falls deren Konfiguration fehlt.
2. `web`-Netzwerk prüfen.
3. Ollama-Stack mit derselben `.env` bereitstellen.
4. `ollama_data` aus dem Backup wiederherstellen oder benötigte Modelle neu laden.
5. Gruppenbindung in Authentik und externen Zugriff prüfen.

Danach mindestens ausführen:

```bash
docker compose ps
docker compose exec ollama ollama list
```
