# Server konfigurieren

Platzhalter wie `<DOMAIN>`, `<SSH_PORT>` und `<ÖFFENTLICHE_IPV4>` sind vor der Ausführung durch die eigenen Werte zu ersetzen.

## 1. DNS

Die verwendeten öffentlichen Namen stehen in der [Dienste-Übersicht](../dienste.md). Jeder Name benötigt einen passenden DNS-Eintrag, bevor sein Stack gestartet wird.

### Einzelne Einträge

```text
<SUBDOMAIN>      A       <ÖFFENTLICHE_IPV4>
<SUBDOMAIN>      AAAA    <ÖFFENTLICHE_IPV6>
```

### Wildcard

Alternativ kann ein bewusst verwendeter Wildcard-Eintrag die Subdomains abdecken:

```text
*         A       <ÖFFENTLICHE_IPV4>
*         AAAA    <ÖFFENTLICHE_IPV6>
```

Nur einen AAAA-Eintrag setzen, wenn IPv6 vom Internet aus tatsächlich bis zum Server auf TCP 80 und 443 funktioniert.

Prüfung:

```bash
getent ahostsv4 <ADRESSE>
```

Bei konfiguriertem IPv6:

```bash
getent ahostsv6 <ADRESSE>
```

Erwartet: Die verwendeten Namen liefern die für diesen Server vorgesehenen öffentlichen Adressen.

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

Host-Ports werden nur veröffentlicht, wenn ein Stack sie ausdrücklich benötigt. Die Freigaben stehen in der jeweiligen Stack-Dokumentation.

## 5. Zusätzliche Provider-Firewall (Netcup)

Die Host-Firewall und eine im Netcup-Panel aktivierte Firewall sind zwei
unabhängige Schutzschichten. Die erlaubte Regel `ct state established,related`
in der Host-Firewall ersetzt daher keine Rückverkehr-Regel im Netcup-Panel.

Besonders wichtig: Werden bei Netcup eigene **ausgehende** Regeln angelegt,
gilt für nicht ausdrücklich erlaubten ausgehenden Verkehr implizit `DROP`.
Das betrifft auch Docker-Image-Downloads und die Zeitsynchronisierung.

Bei einer restriktiven Netcup-Konfiguration mit Eingangs- und Ausgangs-Policy
`DROP` müssen mindestens diese Regeln vorhanden sein. Die Regeln sind für IPv4
und IPv6 entsprechend anzulegen.

| Richtung | Protokoll | Quellport | Zielport | Aktion | Zweck |
|---|---|---:|---:|---|---|
| eingehend | TCP | beliebig | `22` | ACCEPT | SSH |
| eingehend | TCP | beliebig | `80`, `443` | ACCEPT | Web und ACME HTTP-01 |
| ein- und ausgehend | ICMP / ICMPv6 | – | – | ACCEPT | Erreichbarkeit und Netzbetrieb |
| ausgehend | UDP | beliebig | `53` | ACCEPT | DNS-Anfrage |
| eingehend | UDP | `53` | beliebig | ACCEPT | DNS-Antwort |
| ausgehend | TCP | beliebig | `53` | ACCEPT | DNS über TCP |
| eingehend | TCP | `53` | beliebig | ACCEPT | DNS-Antwort über TCP |
| ausgehend | UDP | beliebig | `123` | ACCEPT | NTP-Anfrage |
| eingehend | UDP | `123` | beliebig | ACCEPT | NTP-Antwort |
| ausgehend | TCP | beliebig | `80`, `443` | ACCEPT | Updates, Image-Downloads und ACME |
| eingehend | TCP | `80`, `443` | beliebig | ACCEPT | Antworten auf Web-Verbindungen |

Falls SMTP absichtlich unterbunden werden soll, zusätzlich vor einer etwaigen
allgemeinen Ausgangsfreigabe TCP zu den Zielports `25`, `465` und `587` mit
`DROP` sperren.

Nach einer Änderung mindestens beide Prüfungen ausführen:

```bash
timedatectl status
curl -4 -I --connect-timeout 15 https://registry-1.docker.io/v2/
```

Erwartet sind `System clock synchronized: yes` sowie bei Docker Hub ein
HTTP-Status `401`. `401` bedeutet hier, dass die Registry erreichbar ist und
lediglich eine Anmeldung verlangt.

Weitere Details zur Regelreihenfolge und zu Richtungen stehen in der
[Netcup-Firewall-Dokumentation](https://www.netcup.com/de/helpcenter/dokumentation/server/firewall).

## 6. Externes Docker-Netzwerk

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

## 7. Zentrale `.gitignore`

Die versionierte Datei im Repository-Root lautet im aktuellen Projektstand:

```gitignore
# Umgebungsdateien
.env
**/.env

# Secrets
secrets/
**/secrets/

# Logs
*.log

# Traefik ACME-Dateien
acme*.json
```

Sie schützt damit insbesondere die lokalen `.env`-Dateien und alle stacklokalen `secrets/`-Verzeichnisse.

Backups werden in diesem Projekt bewusst **außerhalb des Git-Repositorys** erstellt. Deshalb hängt deren Schutz nicht von zusätzlichen `backups/`- oder Dump-Regeln ab. Siehe [Backup und Wiederherstellung](../backup-und-wiederherstellung.md).

Prüfen:

```bash
cd <PROJEKT_ROOT>

git check-ignore -v \
  Compose/<STACK>/.env \
  Compose/<STACK>/secrets/<SECRET_DATEI>
```

Erwartet: Für jeden Pfad erscheint eine passende Regel aus der zentralen `.gitignore`. Keine Ausgabe für einen Pfad bedeutet, dass dieser nicht ignoriert wird.

## 8. Erreichbarkeit nach Traefik-Start

```bash
sudo ss -lntp | grep -E ':(80|443)\s'
```

Nach dem Core-Start von extern testen:

```bash
curl -I http://auth.<DOMAIN>
```

Erwartet wird `301` oder `308` und ein `Location`-Header mit der entsprechenden `https://`-Adresse. Weitere Dienste gemäß [Dienste-Übersicht](../dienste.md) einzeln prüfen.

## 9. Neustarttest

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
