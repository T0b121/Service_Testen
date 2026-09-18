# Part-DB-Stack: Betrieb

## 1. Stack-Verzeichnis

```bash
cd <PROJEKT_ROOT>/Compose/partdb
```

## 2. Status

```bash
docker compose ps
```

Erwartet im Normalbetrieb:

```text
partdb-mariadb   ...   healthy
partdb-server    ...   Up
```

Part-DB besitzt in diesem Stack keinen eigenen Docker-Healthcheck. `Up` ist daher der vorgesehene Status.

## 3. Starten

Vorhandene Container:

```bash
docker compose start
```

Fehlende oder aufgrund der Konfiguration neu zu erstellende Container:

```bash
docker compose up -d
```

## 4. Stoppen

```bash
docker compose stop
```

Die Container bleiben vorhanden; Volumes und Daten bleiben erhalten.

## 5. Container entfernen, Daten behalten

```bash
docker compose down
```

Die benannten Volumes bleiben erhalten.

Nicht als normalen Betriebsbefehl verwenden:

```bash
docker compose down -v
```

`-v` löscht die Stack-Volumes und damit Datenbank, Uploads und öffentliche Medien.

## 6. Neustart

Beide Dienste:

```bash
docker compose restart
```

Nur Part-DB:

```bash
docker compose restart partdb
```

Bei Änderungen an `.env`, Secret-Mounts oder Compose-Konfiguration reicht `restart` nicht, weil der vorhandene Container seine Umgebung behält. Dann:

```bash
docker compose config --quiet
docker compose up -d
```

Für eine Änderung an einem Part-DB-Env-Wert genügt normalerweise:

```bash
docker compose up -d --force-recreate partdb
```

## 7. Logs

Alle Dienste:

```bash
docker compose logs --tail=150
```

Part-DB:

```bash
docker compose logs --tail=200 partdb
```

MariaDB:

```bash
docker compose logs --tail=200 mariadb
```

Live:

```bash
docker compose logs -f
```

`Ctrl+C` beendet nur die Loganzeige.

## 8. MariaDB-Healthcheck

```bash
docker compose exec mariadb \
  healthcheck.sh \
  --connect \
  --innodb_initialized
```

Docker-Status:

```bash
docker inspect partdb-mariadb \
  --format '{{json .State.Health}}'
```

## 9. Webzugriff prüfen

HTTP-Redirect:

```bash
curl -I http://partdb.<DOMAIN>
```

Erwartet: `301` oder `308` auf HTTPS.

Unauthentifizierter HTTPS-Test bei Produktionszertifikaten:

```bash
curl -I https://partdb.<DOMAIN>/
```

Bei Staging:

```bash
curl -k -I https://partdb.<DOMAIN>/
```

Erwartet ist normalerweise eine `302`-Weiterleitung zu Authentik. Ein `200` mit direkt lesbarer Part-DB-Seite ohne Authentik-Sitzung wäre ein Sicherheitsfehler.

## 10. Outpost prüfen

Produktion:

```bash
curl -I \
  https://partdb.<DOMAIN>/outpost.goauthentik.io/ping
```

Staging:

```bash
curl -k -I \
  https://partdb.<DOMAIN>/outpost.goauthentik.io/ping
```

Erwartet:

```text
HTTP/2 204
```

## 11. Browser-Funktionstest

Nach Änderungen oder Updates mindestens:

1. privates Browserfenster öffnen,
2. `https://partdb.<DOMAIN>/` aufrufen,
3. Authentik-Weiterleitung kontrollieren,
4. SAML-Anmeldung in Part-DB ausführen,
5. Partliste öffnen,
6. mit einem passenden Benutzer eine erlaubte Aktion testen,
7. Read-only- und Negativtest kontrollieren, wenn Berechtigungen betroffen waren.

## 12. Netzwerke

```bash
docker network inspect web
docker network inspect partdb_internal
```

Erwartet:

- `partdb-server` in `web`,
- `partdb-server` und `partdb-mariadb` in `partdb_internal`,
- `partdb-mariadb` **nicht** in `web`.

## 13. Volumes

```bash
docker volume inspect partdb_uploads
docker volume inspect partdb_public_media
docker volume inspect partdb_mariadb_data
```

Nicht manuell in `/var/lib/docker/volumes/` schreiben. Für Sicherung und Restore die dokumentierten Verfahren verwenden.

## 14. PHP-Konfiguration prüfen

```bash
docker compose exec partdb \
  php -i \
  | grep '^max_input_vars'
```

Erwartet:

```text
max_input_vars => 10000 => 10000
```

Der Wert stammt aus der versionierten `config/zz-partdb.ini` und muss nicht pro Installation geändert werden.

## 15. Konsolenbefehle

Allgemeines Muster:

```bash
docker compose exec partdb \
  /partdb-secret-entrypoint.sh \
  console <BEFEHL>
```

Beispiele:

```bash
docker compose exec partdb \
  /partdb-secret-entrypoint.sh \
  console partdb:users:list

docker compose exec partdb \
  /partdb-secret-entrypoint.sh \
  console cache:clear
```

Der Wrapper lädt dieselben Secrets und Konfigurationswerte wie beim normalen Part-DB-Start.

## 16. `.env` ändern

Vorher eine geschützte Kopie **außerhalb des Git-Repositorys** anlegen:

```bash
umask 077
ENV_BACKUP="$HOME/partdb-env.$(date -u +%Y%m%dT%H%M%SZ).bak"
cp .env "$ENV_BACKUP"
printf 'Sicherung: %s\n' "$ENV_BACKUP"
```

Keine `.env.bak.*`-Datei direkt im Stack-Verzeichnis erzeugen; solche Namen werden von der aktuellen `.gitignore` nicht automatisch erfasst.

Änderung vornehmen, anschließend:

```bash
docker compose config --quiet
docker compose up -d --force-recreate partdb
docker compose ps
docker compose logs --tail=150 partdb
```

Datenbankname, Datenbankbenutzer oder Passwörter nicht blind ändern. Diese Werte sind mit dem bestehenden MariaDB-Datenbestand verknüpft.

## 17. Secret-Dateien

Vorhandensein und Rechte prüfen, ohne Inhalte auszugeben:

```bash
stat -c '%A %s Bytes %n' secrets/*
```

Erwartet: Secret-Dateien sind nur für den Besitzer lesbar und schreibbar (`-rw-------`).

Ein neues Secret in einer Datei bedeutet nicht automatisch, dass der bestehende Gegenpart dasselbe Secret kennt. Besonders Datenbankpasswörter und SAML-Schlüssel benötigen einen geplanten Rotationsablauf.

## 18. Images aktualisieren

Vor jedem Update:

- Release Notes lesen,
- [Backup](backup-und-wiederherstellung.md) erstellen,
- aktuelle Image-Tags und Digests dokumentieren.

Danach gemäß [Wartung und Updates](../../wartung-und-updates.md).

Besonderheit: `DB_AUTOMIGRATE=true` kann beim Start nach einem Part-DB-Update Datenbankmigrationen ausführen. Deshalb Logs nach jedem Update beobachten.

Eine MariaDB-Haupt- oder Versionslinienänderung ist kein normales Image-Update. Vorher MariaDB- und Part-DB-Kompatibilität prüfen, einen vollständigen SQL-Dump sowie die Volumes sichern und einen Rollbackplan festlegen. Datenbanksecrets nicht nebenbei rotieren.

## 19. Geplanter Host-Neustart

Vorher:

```bash
docker compose ps
```

Nachher:

```bash
docker compose ps
systemctl is-active docker
systemctl is-active nftables
curl -I http://partdb.<DOMAIN>
```

Danach Browser-Login und SAML testen.

## 20. Regelmäßige Kontrollen

```bash
docker compose ps
docker compose logs --since=24h
docker system df
df -h
```

Zusätzlich regelmäßig prüfen:

- Backupalter und Restore-Test,
- Part-DB- und MariaDB-Updatehinweise,
- SAML-SP-Zertifikatsablauf,
- Authentik-Signing-Zertifikat,
- Mitglieder der drei `partdb-*`-Gruppen,
- anonyme Part-DB-Rechte,
- Part-DB-Ereignislog,
- freier Speicher in Datenbank- und Uploadvolumes.
