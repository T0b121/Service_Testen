# Server konfigurieren

Platzhalter wie `<DOMAIN>`, `<SSH_PORT>` und `<ÖFFENTLICHE_IPV4>` sind vor der Ausführung durch die eigenen Werte zu ersetzen.

## 1. DNS

Für den Core-Stack werden benötigt:

```text
auth.<DOMAIN>
proxy.<DOMAIN>
```

### Einzelne Einträge

```text
auth     A       <ÖFFENTLICHE_IPV4>
proxy    A       <ÖFFENTLICHE_IPV4>

auth     AAAA    <ÖFFENTLICHE_IPV6>
proxy    AAAA    <ÖFFENTLICHE_IPV6>
```

### Wildcard

```text
*        A       <ÖFFENTLICHE_IPV4>
*        AAAA    <ÖFFENTLICHE_IPV6>
```

Nur einen AAAA-Eintrag setzen, wenn IPv6 vom Internet aus bis zum Server funktioniert.

Prüfung:

```bash
getent ahostsv4 auth.<DOMAIN>
getent ahostsv4 proxy.<DOMAIN>

getent ahostsv6 auth.<DOMAIN>
getent ahostsv6 proxy.<DOMAIN>
```

Erwartet: `auth.<DOMAIN>` und `proxy.<DOMAIN>` liefern dieselbe öffentliche IPv4-Adresse. Bei konfiguriertem AAAA-Eintrag müssen beide Namen außerdem die öffentliche IPv6-Adresse liefern.

Serveradressen:

```bash
ip -4 addr show scope global
ip -6 addr show scope global
```

Die DNS-Ergebnisse müssen zu den für den Server vorgesehenen öffentlichen Adressen passen. Private Adressen aus Docker-Netzwerken wie `172.x.x.x` sind keine öffentlichen DNS-Ziele.

## 2. Ports

Benötigt:

| Port | Protokoll | Zweck |
|---:|---|---|
| `<SSH_PORT>` | TCP | Administration |
| `80` | TCP | HTTP-Redirect und ACME HTTP-01 |
| `443` | TCP | HTTPS |

Belegung prüfen:

```bash
sudo ss -lntp | grep -E ':(80|443)\s' || true
```

Erwartet vor dem ersten Traefik-Start: keine Ausgabe. Nach dem Start müssen beide Ports durch Docker beziehungsweise Traefik belegt sein.

## 3. Persistente nftables-Konfiguration

Das folgende Beispiel schützt Hostdienste. Port `22` ist durch den tatsächlich verwendeten SSH-Port zu ersetzen.

Datei sichern:

```bash
sudo cp /etc/nftables.conf /etc/nftables.conf.bak
```

`/etc/nftables.conf`:

```nft
#!/usr/sbin/nft -f

table inet host_firewall
flush table inet host_firewall

table inet host_firewall {
    chain input {
        type filter hook input priority filter;
        policy drop;

        iifname "lo" accept

        ct state established,related accept
        ct state invalid drop

        ip protocol icmp accept
        ip6 nexthdr ipv6-icmp accept

        tcp dport { 22, 80, 443 } accept
    }
}
```

Warum die ersten beiden Zeilen?

```nft
table inet host_firewall
flush table inet host_firewall
```

Sie machen wiederholtes Laden idempotent:

- Tabelle bei Bedarf anlegen.
- nur die eigene Tabelle leeren.
- Regeln anschließend genau einmal neu erstellen.
- Docker-Tabellen nicht löschen.

Syntax prüfen:

```bash
sudo nft -c -f /etc/nftables.conf
```

Bei Erfolg erfolgt keine Ausgabe.

Während eine SSH-Sitzung geöffnet bleibt:

```bash
sudo systemctl reload nftables
```

Kontrolle:

```bash
sudo nft list table inet host_firewall
```

Erwartet: genau eine `input`-Chain mit Policy `drop` und je einer Regel für Loopback, bestehende Verbindungen, ungültige Pakete, ICMP, ICMPv6 sowie die freigegebenen TCP-Ports. Der Regelblock darf nach einem Reload nicht doppelt erscheinen.

### Nicht `restart` verwenden, ohne Docker zu beachten

Der Standarddienst kann beim Stoppen das gesamte nftables-Ruleset leeren. Nach einem `systemctl restart nftables` können deshalb von Docker erzeugte Regeln fehlen.

Für Regeländerungen bevorzugt:

```bash
sudo systemctl reload nftables
```

Falls nftables tatsächlich neu gestartet wurde:

```bash
sudo systemctl restart docker
```

Danach Container und Netzwerke prüfen.

## 4. Docker-Firewallregeln

Docker erzeugt eigene NAT- und Filterregeln. Meldungen wie diese sind erwartbar:

```text
table ip nat is managed by iptables-nft, do not touch
table ip filter is managed by iptables-nft, do not touch
```

Diese Tabellen nicht manuell bearbeiten.

Prüfung:

```bash
sudo nft list table ip nat >/dev/null \
  && echo "Docker-NAT vorhanden"

sudo nft list table ip filter >/dev/null \
  && echo "Docker-Filter vorhanden"
```

Wichtig: Veröffentlichte Docker-Ports werden über Forwarding und NAT verarbeitet und können die normale Host-`input`-Chain umgehen. Deshalb ist die wichtigste Regel des Projekts:

> Nur Dienste veröffentlichen, die wirklich öffentlich erreichbar sein müssen.

Im Core-Stack veröffentlicht ausschließlich Traefik TCP 80 und 443.

## 5. Externes Docker-Netzwerk

Einmalig erstellen:

```bash
docker network create web
```

Falls es bereits existiert, prüfen:

```bash
docker network inspect web \
  --format 'Name={{.Name}} Driver={{.Driver}} Scope={{.Scope}}'
```

Erwartet:

```text
Name=web Driver=bridge Scope=local
```

Das Netzwerk wird außerhalb einzelner Compose-Stacks verwaltet, damit weitere Stacks Traefik erreichen können.

## 6. Zentrale `.gitignore`

Im Repository-Root:

```gitignore
# Umgebungsdateien
.env
**/.env

# Secrets
secrets/
**/secrets/

# Logs
*.log

# Lokale ACME-Dateien bei Bind-Mounts
acme*.json

# Backups und Dumps
backups/
**/backups/
*.dump
*.backup
```

Prüfen:

```bash
cd <PROJEKT_ROOT>

git check-ignore -v Compose/core/.env
git check-ignore -v Compose/core/secrets/authentik_secret_key
```

Erwartet: Für beide Pfade erscheint eine passende Regel aus der zentralen `.gitignore`. Keine Ausgabe bedeutet, dass der jeweilige Pfad nicht ignoriert wird.

## 7. Erreichbarkeit nach Traefik-Start

```bash
sudo ss -lntp | grep -E ':(80|443)\s'
```

Von extern testen:

```bash
curl -I http://auth.<DOMAIN>
curl -I http://proxy.<DOMAIN>/dashboard/
```

Erwartet wird für beide Aufrufe `301` oder `308` und ein `Location`-Header mit der jeweiligen `https://`-Adresse.

## 8. Neustarttest

Nach vollständiger Einrichtung:

```bash
sudo reboot
```

Danach:

```bash
systemctl is-active docker
systemctl is-active nftables
docker ps
sudo nft list table inet host_firewall
```

Erwartet:

- Docker und nftables melden `active`.
- die vorgesehenen Container laufen.
- die eigene Firewalltabelle enthält den Regelblock genau einmal.

## Offizielle Referenzen

- [Docker Packet Filtering und Firewalls](https://docs.docker.com/engine/network/packet-filtering-firewalls/)
- [Docker Port Publishing](https://docs.docker.com/engine/network/port-publishing/)
