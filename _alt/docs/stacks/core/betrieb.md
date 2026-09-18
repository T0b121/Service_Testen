# Core-Stack: Betrieb

## 1. Stack-Verzeichnis

```bash
cd <PROJEKT_ROOT>/Compose/core
```

## 2. Status

```bash
docker compose ps
```

Erwartet:

```text
postgresql         healthy
authentik-server   healthy
authentik-worker   healthy
traefik            healthy
```

## 3. Starten

Vorhandene Container:

```bash
docker compose start
```

Fehlende oder geänderte Container erstellen:

```bash
docker compose up -d
```

## 4. Stoppen

```bash
docker compose stop
```

Container bleiben vorhanden.

## 5. Container entfernen, Daten behalten

```bash
docker compose down
```

Benannte Volumes bleiben erhalten.

Nicht als normalen Betriebsbefehl verwenden:

```bash
docker compose down -v
```

`-v` löscht die Stack-Volumes und damit Daten.

## 6. Neustart

Alle Dienste:

```bash
docker compose restart
```

Ein Dienst:

```bash
docker compose restart traefik
```

Bei Änderungen an `compose.yml` oder `.env` ist `restart` nicht ausreichend. Dann:

```bash
docker compose config --quiet
docker compose up -d
```

## 7. Einzelnen Dienst neu erstellen

```bash
docker compose up -d --force-recreate traefik
```

Oder:

```bash
docker compose up -d --force-recreate authentik-server
```

## 8. Logs

Alle:

```bash
docker compose logs --tail=100
```

Ein Dienst:

```bash
docker compose logs --tail=100 traefik
```

Seit einem Zeitraum:

```bash
docker compose logs --since=15m authentik-server
```

Live:

```bash
docker compose logs -f
```

`Ctrl+C` beendet nur die Anzeige.

## 9. Healthchecks

```bash
docker compose ps
```

Traefik manuell:

```bash
docker exec core-traefik \
  traefik healthcheck \
  --ping=true \
  --ping.entrypoint=ping \
  --entrypoints.ping.address=:8082
```

PostgreSQL:

```bash
docker compose exec postgresql \
  sh -c 'pg_isready -d "$POSTGRES_DB" -U "$POSTGRES_USER"'
```

## 10. HTTP-Prüfungen

```bash
curl -I http://auth.<DOMAIN>
curl -I http://proxy.<DOMAIN>/dashboard/
```

Erwartet: `301` oder `308` mit `Location: https://...`.

Staging-HTTPS:

```bash
curl -k -I https://auth.<DOMAIN>
```

Erwartet: `200` oder eine beabsichtigte `302`-Weiterleitung; kein `404`, `502` oder Verbindungsfehler.

Outpost:

```bash
curl -k -I \
  https://auth.<DOMAIN>/outpost.goauthentik.io/ping
```

Erwartet:

```text
HTTP/2 204
```

## 11. Netzwerke

```bash
docker network inspect web
docker network inspect core_auth
```

Worker und PostgreSQL dürfen nicht in `web` erscheinen.

## 12. Volumes

```bash
docker volume inspect core_postgresql_data
docker volume inspect core_authentik_data
```

Aktives ACME-Volume:

```bash
docker compose config \
  | grep -A3 'traefik_acme:'
```

## 13. Konfigurationsänderung

```bash
docker compose config --quiet
docker compose up -d
docker compose ps
docker compose logs --tail=100
```

Danach Funktionstest.

## 14. Images aktualisieren

Siehe:

- [Wartung und Updates](../../wartung-und-updates.md)

Kurzablauf nach Backup:

```bash
docker compose pull
docker compose up -d
docker compose ps
docker compose logs --tail=150
```

## 15. Staging und Produktion

Der aktive ACME-Modus wird ausschließlich über `.env` ausgewählt.

Details:

- [TLS und Zertifikate](../../tls-und-zertifikate.md)

## 16. Geplanter Neustart des Hosts

Vorher:

```bash
docker compose ps
sudo nft list table inet host_firewall
```

Danach:

```bash
docker compose ps
systemctl is-active docker
systemctl is-active nftables
curl -I http://auth.<DOMAIN>
```

## 17. Regelmäßige Kontrolle

```bash
docker compose ps
docker compose logs --since=24h
docker system df
df -h
```

In Authentik:

- fehlgeschlagene Tasks
- ungewöhnliche Loginereignisse
- Admin-Gruppenmitgliedschaft
- Outpost-Gesundheit
