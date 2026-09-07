# Uptime-Kuma-Stack: Vorbereiten

Vorher abschließen:

- [Core-Stack: Erststart und Prüfung](../core/erststart-und-pruefung.md)

## 1. Versionierte Dateien prüfen

```bash
cd <PROJEKT_ROOT>
git ls-files 'Compose/uptime-kuma/*' | sort
```

Erwartet:

```text
Compose/uptime-kuma/compose.yml
```

## 2. Lokale `.env` anlegen

```bash
cd <PROJEKT_ROOT>/Compose/uptime-kuma
nano .env
```

Inhalt:

```dotenv
# Basisdomain; die öffentliche Adresse lautet uptime.${DOMAIN}.
DOMAIN=<DOMAIN>

# Stabile Uptime-Kuma-Hauptlinie. "2" übernimmt neue stabile 2.x-Releases,
# aber kein späteres Hauptversions-Upgrade.
UPTIME_KUMA_VERSION=2
```

`UPTIME_KUMA_VERSION=2` ist der vom Uptime-Kuma-Projekt dokumentierte
Container-Tag. Vor jedem Update müssen trotzdem Release Notes und das Backup
geprüft werden.

Dateirechte und Git-Schutz prüfen:

```bash
chmod 600 .env
stat -c '%A %n' .env
git check-ignore -v .env
```

Erwartet: `-rw-------` und eine passende `.gitignore`-Regel.

## 3. Verzeichnis für den lokalen Notfallzugang vorbereiten

Der lokale Kuma-Administrator ist unabhängig von Authentik. Sein Passwort
gehört ausschließlich in eine ignorierte Secret-Datei:

```bash
cd <PROJEKT_ROOT>/Compose/uptime-kuma
mkdir -p secrets
chmod 700 secrets
```

Die eingerichtete Instanz verwendet:

```text
Benutzername: kuma-admin
Passwortdatei: secrets/uptime_kuma_admin_password
```

Die Datei muss `0600` haben und gehört in einen Passwortmanager oder ein
verschlüsseltes Backup. Sie darf nicht eingecheckt werden.

## 4. DNS und Netzwerk prüfen

```bash
cd <PROJEKT_ROOT>
getent ahostsv4 uptime.<DOMAIN>
getent ahostsv6 uptime.<DOMAIN>
docker network inspect web --format 'Name={{.Name}} Driver={{.Driver}} Scope={{.Scope}}'
```

DNS muss auf die öffentlichen Serveradressen zeigen. Bei bewusst nicht
verwendetem IPv6 darf die IPv6-Abfrage ohne Ausgabe bleiben. Für das Netzwerk
wird `Name=web Driver=bridge Scope=local` erwartet.

## 5. Konfiguration prüfen

```bash
cd <PROJEKT_ROOT>/Compose/uptime-kuma
docker compose config --quiet
```

Erwartet: keine Ausgabe und Exit-Code `0`. Es darf kein `ports:`-Mapping
geben; `expose: 3001` ist dagegen erwartet.

Weiter mit [Authentik einrichten](authentik-einrichten.md).
