# Jellyfin-Stack: Vorbereiten

Vorher abschließen:

- [Server konfigurieren](../../server/konfigurieren.md)
- [Core-Stack: Erststart und Prüfung](../core/erststart-und-pruefung.md)

## 1. Versionierte Datei prüfen

```bash
cd <PROJEKT_ROOT>
git ls-files 'Compose/jellyfin/*' | sort
```

Erwartet:

```text
Compose/jellyfin/compose.yml
```

## 2. Lokale `.env` anlegen

```bash
cd <PROJEKT_ROOT>/Compose/jellyfin
nano .env
```

Inhalt:

```dotenv
# Basisdomain; die öffentliche Adresse lautet jellyfin.${DOMAIN}.
DOMAIN=<DOMAIN>

# Stabile Jellyfin-Patch-Linie. "10.11" übernimmt nur 10.11.x-Updates,
# aber kein Upgrade auf Jellyfin 12.
JELLYFIN_VERSION=10.11
```

`JELLYFIN_VERSION=10.11` ist bewusst ein Versionslinien-Tag. Ein
`docker compose pull` kann damit Bugfix-Releases wie `10.11.11` laden, aber
keine Vorabversion und keine neue Haupt- oder Nebenversion.

Dateirechte und Git-Schutz prüfen:

```bash
chmod 600 .env
stat -c '%A %n' .env
git check-ignore -v .env
```

Erwartet: `-rw-------` und eine passende `.gitignore`-Regel.

## 3. DNS und Netzwerk prüfen

```bash
cd <PROJEKT_ROOT>
getent ahostsv4 jellyfin.<DOMAIN>
getent ahostsv6 jellyfin.<DOMAIN>
docker network inspect web --format 'Name={{.Name}} Driver={{.Driver}} Scope={{.Scope}}'
```

DNS muss auf die öffentlichen Serveradressen zeigen. Bei bewusst nicht
verwendetem IPv6 darf die IPv6-Abfrage ohne Ausgabe bleiben. Für das Netzwerk
wird `Name=web Driver=bridge Scope=local` erwartet.

## 4. CPU-Transcoding bewusst verwenden

```bash
ls -l /dev/dri/
```

Aktuell ist nur `card0` vorhanden; ein für Jellyfin notwendiges
`renderD*`-Gerät fehlt. Deshalb enthält die Compose-Datei absichtlich kein
`devices:`-Mapping. CPU-Transcoding funktioniert ohne weitere Einrichtung,
kann bei hohen Auflösungen jedoch rechenintensiv sein.

## 5. Konfiguration prüfen

```bash
cd <PROJEKT_ROOT>/Compose/jellyfin
docker compose config --quiet
```

Erwartet: keine Ausgabe und Exit-Code `0`. Es darf kein `ports:`-Mapping
geben; `expose: 8096` ist dagegen erwartet.

Weiter mit [Authentik einrichten](authentik-einrichten.md).
