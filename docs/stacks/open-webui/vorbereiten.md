# Open-WebUI-Stack: Vorbereiten

Vorher abschließen:

- [Core-Stack: Erststart und Prüfung](../core/erststart-und-pruefung.md)
- [Ollama-Stack: Erststart und Prüfung](../ollama/erststart-und-pruefung.md)
- [SearXNG-Stack: Erststart und Prüfung](../searxng/erststart-und-pruefung.md)

## 1. Versionierte Dateien prüfen

```bash
cd <PROJEKT_ROOT>

git ls-files 'Compose/open-webui/*' | sort
```

Erwartet:

```text
Compose/open-webui/compose.local-auth.yml
Compose/open-webui/compose.yml
```

Das Installationsverfahren verändert diese versionierten Dateien nicht.

## 2. DNS prüfen

```bash
getent ahostsv4 webui.<DOMAIN>
getent ahostsv6 webui.<DOMAIN>
```

Die Ergebnisse müssen auf die öffentlichen Serveradressen zeigen. Bei bewusst
nicht verwendetem IPv6 darf die IPv6-Abfrage ohne Ausgabe bleiben.

## 3. Netzwerk prüfen

```bash
docker network inspect web \
  --format 'Name={{.Name}} Driver={{.Driver}} Scope={{.Scope}}'
docker network inspect searxng_clients \
  --format 'Name={{.Name}} Driver={{.Driver}} Scope={{.Scope}} Internal={{.Internal}}'
```

Erwartet:

```text
Name=web Driver=bridge Scope=local
Name=searxng_clients Driver=bridge Scope=local Internal=true
```

## 4. Lokale `.env` anlegen

```bash
cd <PROJEKT_ROOT>/Compose/open-webui
nano .env
```

Inhalt für die Standardkonfiguration mit Authentik-OIDC:

```dotenv
# Domain
DOMAIN=<DOMAIN>

# Docker Image Version
# Bewusst kein latest-Tag verwenden.
OPEN_WEBUI_VERSION=v0.11.0

# Authentik-OIDC-Provider; Werte nach dessen Anlage eintragen.
OPENWEBUI_OIDC_CLIENT_ID=<CLIENT_ID>
OPENWEBUI_OIDC_CLIENT_SECRET=<CLIENT_SECRET>

```

`DOMAIN` enthält nur die Basisdomain ohne Protokoll oder Subdomain. Daraus
entsteht die feste öffentliche Adresse `https://webui.<DOMAIN>`.

`OPEN_WEBUI_VERSION` wird bei geplanten Updates bewusst angepasst. Kein
`latest`-Tag verwenden. Die beiden OIDC-Werte stellt Authentik beim Anlegen
des Providers bereit. Das Client-Secret ist vertraulich und bleibt ausschließlich
in dieser lokalen Datei.

### Alternative ohne OIDC

Die Standardkonfiguration verwendet OIDC. Für Authentik Forward Auth mit
lokalen Open-WebUI-Konten die zwei OIDC-Variablen aus `.env` entfernen und alle
nachfolgenden Compose-Befehle mit dem versionierten Override ausführen:

```bash
docker compose -f compose.yml -f compose.local-auth.yml config --quiet
```

Die vollständige Provider-Konfiguration steht in
[Ohne OIDC einrichten](authentik-einrichten-ohne-oidc.md). Nicht zwischen
beiden Betriebsarten umschalten, solange Daten im Volume erhalten bleiben;
dafür einen bewussten Migrations- oder Neuinstallationsschritt durchführen.

Dateirechte und Git-Schutz prüfen:

```bash
chmod 600 .env
stat -c '%A %n' .env
git check-ignore -v .env
```

Erwartet: `-rw-------` und eine passende `.gitignore`-Regel.

## 5. Secret-Verzeichnis anlegen

```bash
mkdir -p secrets
chmod 700 secrets
```

Der lokale Open-WebUI-Signierschlüssel wird nach der Authentik-Einrichtung im
nächsten Dokument angelegt. Seine Inhalte niemals mit `cat`, `echo` oder in
Supportausgaben anzeigen.

Weiter mit [Authentik einrichten](authentik-einrichten.md).
