# Server-Fehlerbehebung

## 1. Diagnosebasis

```bash
cat /etc/os-release
docker --version
docker compose version
git --version
sudo nft --version

systemctl is-active docker
systemctl is-active nftables
sudo systemctl --failed
```

## 2. `docker: command not found`

Docker ist nicht installiert oder nicht im PATH.

```bash
command -v docker
```

Die Installationsanleitung der Distribution beziehungsweise die offizielle Docker-Anleitung verwenden.

## 3. `docker compose` fehlt

```bash
docker compose version
```

Nicht den veralteten Standalone-Befehl `docker-compose` voraussetzen. Auf Linux das Compose-Plugin installieren.

## 4. Zugriff auf Docker verweigert

```text
permission denied while trying to connect to the Docker daemon socket
```

Prüfen:

```bash
systemctl is-active docker
ls -l /var/run/docker.sock
id
getent group docker
```

Nach Gruppenänderung vollständig neu anmelden.

## 5. `nft: command not found`

Wenn `sudo nft` funktioniert, liegt `/usr/sbin` wahrscheinlich nicht im Benutzer-PATH.

```bash
sudo command -v nft
sudo nft --version
```

## 6. nftables-Regeln erscheinen mehrfach

Ursache: Eine Datei mit `nft -f` wiederholt geladen, ohne die eigene Tabelle vorher zu leeren.

Idempotentes Muster:

```nft
table inet host_firewall
flush table inet host_firewall

table inet host_firewall {
    ...
}
```

Danach:

```bash
sudo nft -c -f /etc/nftables.conf
sudo systemctl reload nftables
```

## 7. Docker-Tabellenwarnung

```text
table ip nat is managed by iptables-nft, do not touch
```

Das ist beim Anzeigen normal. Die Docker-Tabellen nicht bearbeiten.

## 8. Docker-Netzwerk funktioniert nach nftables-Neustart nicht

Der nftables-Dienst kann beim Stoppen das gesamte Ruleset löschen.

```bash
sudo systemctl restart docker
docker network ls
docker ps
```

Für normale Firewalländerungen `reload` statt `restart` verwenden.

## 9. Port 80 oder 443 belegt

```bash
sudo ss -lntp | grep -E ':(80|443)\s'
```

Häufige Ursachen:

- Apache
- nginx
- Caddy
- alter Traefik-Container
- anderer Docker-Stack

Belegenden Dienst kontrolliert stoppen oder Architektur anpassen.

## 10. DNS zeigt auf falsche Adresse

```bash
getent ahostsv4 auth.<DOMAIN>
getent ahostsv6 auth.<DOMAIN>
```

Mit Serveradressen vergleichen:

```bash
ip -4 addr show scope global
ip -6 addr show scope global
```

DNS-TTL beachten.

## 11. IPv4 funktioniert, HTTPS teilweise nicht

Mögliche Ursache: Ein AAAA-Eintrag zeigt auf nicht erreichbares IPv6.

Extern prüfen:

```bash
curl -4 -I http://auth.<DOMAIN>
curl -6 -I http://auth.<DOMAIN>
```

AAAA korrigieren oder entfernen, falls IPv6 nicht betrieben wird.

## 12. Firewall lädt nicht

Syntax:

```bash
sudo nft -c -f /etc/nftables.conf
```

Sicherung wiederherstellen:

```bash
sudo cp /etc/nftables.conf.bak /etc/nftables.conf
```

Keine SSH-Sitzung schließen, solange eine neue Anmeldung nicht getestet wurde.

## 13. Speicher voll

```bash
df -h
df -i
docker system df
```

Große Logs:

```bash
sudo du -xhd1 /var/lib/docker | sort -h
sudo journalctl --disk-usage
```

Nicht blind Volumes löschen.

## 14. Externes Netzwerk fehlt

```bash
docker network inspect web
```

Falls nicht vorhanden:

```bash
docker network create web
```

## 15. Git ignoriert Secrets nicht

```bash
git check-ignore -v \
  Compose/core/.env \
  Compose/core/secrets/authentik_secret_key
```

Bereits eingecheckte Dateien müssen zusätzlich aus dem Git-Index entfernt und gegebenenfalls Secrets rotiert werden.

## 16. Host erreichbar, Docker-Port nicht

Prüfen:

```bash
docker ps
sudo ss -lntp
sudo nft list ruleset
sudo iptables -S DOCKER-USER
```

Docker veröffentlicht Ports über Forwarding/NAT. Nur die Host-`input`-Chain zu prüfen reicht nicht immer aus.
