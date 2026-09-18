# Uptime-Kuma-Stack: Fehlerbehebung

## Container wird nicht `healthy`

```bash
cd <PROJEKT_ROOT>/Compose/uptime-kuma
docker compose ps
docker compose logs --tail=200 uptime-kuma
```

Beim ersten Start kann der Healthcheck bis zu drei Minuten benötigen. Bleibt
der Status danach fehlerhaft, Volume-Füllstand und Logs prüfen:

```bash
docker volume inspect uptime_kuma_data
df -h
```

Das Volume nicht löschen; es enthält die gesamte Konfiguration.

Bei einer neuen Installation muss im Log `Database Type: embedded-mariadb`
stehen. Ein anderer Datenbanktyp bedeutet, dass die Instanz nicht der
Stackkonfiguration entspricht.

## Weiße Seite oder Socket-Verbindungsfehler hinter Traefik und Authentik

Uptime Kuma verwendet WebSockets. Prüfen:

```bash
curl -I https://uptime.<DOMAIN>/outpost.goauthentik.io/ping
docker compose logs --tail=150 uptime-kuma
cd <PROJEKT_ROOT>/Compose/core
docker compose logs --tail=150 traefik
```

Der Outpost-Ping muss `204` liefern. Die Compose-Datei enthält keine eigene
WebSocket-Middleware, weil Traefik WebSocket-Upgrades beim normalen HTTP-Router
automatisch weiterleitet. Bei einer fehlerhaften oder abgelaufenen
Authentik-Sitzung zuerst im Browser vollständig ab- und wieder anmelden.

## Authentik verweigert den Zugriff

Prüfen, ob der Benutzer Mitglied von `uptime-kuma-users` ist und ob die
Gruppenbindung der Anwendung aktiv ist. Anschließend den Embedded Outpost
öffnen und kontrollieren, dass **Uptime Kuma Access Provider** zugewiesen ist.

Die vollständige Sollkonfiguration steht unter
[Authentik einrichten](authentik-einrichten.md).

## Uptime Kuma erreicht ein Ziel nicht

Der Uptime-Kuma-Container ist absichtlich nur im Netzwerk `web`. Ein Ziel in
einem fremden privaten Netzwerk ist nicht automatisch erreichbar. Stattdessen
entweder einen bereits vorgesehenen internen Gesundheitsendpunkt verwenden
oder bewusst einen sicheren Monitor über die öffentliche HTTPS-Adresse
anlegen. Private Datenbanken und Cache-Dienste werden nicht in `web`
aufgenommen, nur damit Uptime Kuma sie überwachen kann.

## Lokalen Uptime-Kuma-Login vergessen

Nicht das Volume löschen. Zuerst einen aktuellen Backupstand prüfen und den
offiziellen Uptime-Kuma-Reset-Ablauf für die tatsächlich installierte Version
nachschlagen. Der lokale Benutzer ist von Authentik unabhängig; eine
Authentik-Gruppenänderung setzt sein Passwort nicht zurück.
