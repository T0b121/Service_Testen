# Server vorbereiten

Die Container sollen auf unterschiedlichen Linux-Distributionen laufen können. Die Struktur und Prüfungen sind distributionsunabhängig; konkrete Paketbefehle unterscheiden sich.

Die getestete Referenzinstallation verwendet Debian 13. Bei anderen Distributionen sind die offiziellen Docker-Anweisungen und der jeweilige Paketmanager zu verwenden.

## 1. Voraussetzungen

Benötigt werden:

- Linux-Server mit Root- oder `sudo`-Zugriff
- funktionierender DNS
- öffentliche IPv4-Adresse
- optional korrekt funktionierendes IPv6
- TCP 22 beziehungsweise eigener SSH-Port
- TCP 80
- TCP 443
- Docker Engine
- Docker Compose V2 als `docker compose`
- Git
- jq
- OpenSSL
- Texteditor, beispielsweise `nano` oder `vi`
- nftables oder eine gleichwertige Host-Firewall
- funktionierende Systemzeit
- ausreichend Speicherplatz
- Git-Repository für das Projekt

Architektur prüfen:

```bash
uname -m
cat /etc/os-release
```

Erwartet: eine von den verwendeten Images unterstützte Architektur, typischerweise `x86_64` oder `aarch64`, sowie eine eindeutig erkennbare Linux-Distribution.

## 2. Vorhandene Installation prüfen

```bash
docker --version
docker compose version
git --version
openssl version
sudo nft --version
```

Dienste:

```bash
systemctl is-enabled docker
systemctl is-active docker
systemctl is-enabled nftables
systemctl is-active nftables
```

Erwartet:

- jeder Versionsbefehl gibt eine Versionsnummer aus,
- `docker compose version` meldet Compose V2,
- Docker und nftables melden jeweils `enabled` und `active`.

Wenn diese Bedingungen erfüllt sind, ist keine Neuinstallation erforderlich.

## 3. Keine Paketquellen mischen

Docker kann aus Distributionspaketen oder aus dem offiziellen Docker-Repository installiert werden. Diese Varianten sollten nicht unkontrolliert gemischt werden.

Vor einer Neuinstallation prüfen:

```bash
dpkg -l | grep -E 'docker|containerd|runc'
```

Eine funktionierende bestehende Installation muss nicht nur wegen abweichender Paketnamen ersetzt werden.

## 4. Debian-13-Beispiel: Grundpakete

```bash
sudo apt update
sudo apt install -y \
  ca-certificates \
  curl \
  git \
  jq \
  nano \
  openssl \
  nftables
```

## 5. Debian-13-Beispiel: Docker aus offiziellem Repository

Nur für eine frische Installation beziehungsweise nach bewusster Bereinigung kollidierender Pakete.

Repository-Schlüssel:

```bash
sudo install -m 0755 -d /etc/apt/keyrings

sudo curl -fsSL \
  https://download.docker.com/linux/debian/gpg \
  -o /etc/apt/keyrings/docker.asc

sudo chmod a+r /etc/apt/keyrings/docker.asc
```

Repository:

```bash
sudo tee /etc/apt/sources.list.d/docker.sources >/dev/null <<EOF
Types: deb
URIs: https://download.docker.com/linux/debian
Suites: $(. /etc/os-release && echo "$VERSION_CODENAME")
Components: stable
Architectures: $(dpkg --print-architecture)
Signed-By: /etc/apt/keyrings/docker.asc
EOF
```

Installation:

```bash
sudo apt update
sudo apt install -y \
  docker-ce \
  docker-ce-cli \
  containerd.io \
  docker-buildx-plugin \
  docker-compose-plugin
```

Start:

```bash
sudo systemctl enable --now docker
```

Test:

```bash
sudo docker run --rm hello-world
docker compose version
```

Erwartet: Der Testcontainer beendet sich erfolgreich und Compose meldet eine Version `2.x` oder neuer.

Für andere Distributionen die offizielle Docker-Anleitung verwenden.

## 6. Docker ohne `sudo`

Optional:

```bash
sudo usermod -aG docker "$USER"
```

Danach vollständig ab- und wieder anmelden.

Test:

```bash
docker info
```

Wichtig: Mitgliedschaft in der Gruppe `docker` entspricht praktisch Root-Rechten auf dem Host. Nur vertrauenswürdige Benutzer aufnehmen.

## 7. nftables aktivieren

```bash
sudo systemctl enable --now nftables
```

Prüfen:

```bash
sudo systemctl status nftables --no-pager
sudo nft list ruleset
```

Erwartet: der Dienst ist `active (exited)` beziehungsweise aktiv, und `nft list ruleset` kann das geladene Regelwerk ohne Fehler anzeigen.

Wenn `nft` ohne `sudo` nicht gefunden wird, liegt es häufig unter `/usr/sbin`, das nicht im normalen Benutzer-PATH enthalten ist. Verwende:

```bash
sudo nft --version
```

## 8. Systemzeit

```bash
timedatectl status
```

Erwartet:

```text
System clock synchronized: yes
```

Falls nicht, Zeitdienst der Distribution aktivieren. Eine falsche Uhrzeit verursacht unter anderem TLS-, OAuth- und SAML-Probleme.

## 9. Speicherplatz

```bash
df -h
df -i
docker system df
```

Für Datenbanken, Images, Uploads und Backups muss Reserve vorhanden sein.

## 10. Git-Repository

Das Projekt-Root ist das Verzeichnis mit:

```text
.git/
.gitignore
README.md
Compose/
docs/
```

Für eine Installation wird der versionierte Repository-Stand verwendet. Auf einem neuen System kann das Repository beispielsweise so geklont werden:

```bash
git clone <REPOSITORY_URL> <PROJEKT_ROOT>
cd <PROJEKT_ROOT>
git status
```

`<REPOSITORY_URL>` ist die Clone-URL dieses Repositorys. `<PROJEKT_ROOT>` ist ein frei wählbarer lokaler Zielpfad und keine feste Vorgabe des Projekts.

Erwartet ist ein sauberer Arbeitsbaum, bevor lokale `.env`- und `secrets/`-Dateien angelegt werden. Diese lokalen Dateien sind durch `.gitignore` geschützt und verändern den Git-Status nicht.

Falls das Repository bewusst neu initialisiert wird:

```bash
mkdir -p <PROJEKT_ROOT>
cd <PROJEKT_ROOT>
git init
```

Die eigentlichen versionierten Projektdateien müssen anschließend aus dem vorgesehenen Repository-Stand übernommen werden; ein leeres `git init` ersetzt sie nicht.

## 11. Lokale Grundstruktur

Die versionierten Verzeichnisse unter `Compose/` und `docs/` kommen aus Git. Lokale Secret-Verzeichnisse werden erst bei der Vorbereitung des jeweiligen Stacks angelegt:

```bash
cd <PROJEKT_ROOT>
ls Compose docs
```

`.env`-Dateien werden erst in den jeweiligen Stack-Anleitungen erzeugt. Die versionierten `compose.yml`, `config/`- und `scripts/`-Dateien werden während einer normalen Installation nicht editiert.

## 12. Abschlussprüfung

```bash
docker --version
docker compose version
git --version
openssl version
sudo nft --version

systemctl is-active docker
systemctl is-active nftables
```

Erwartet: alle Versionsbefehle funktionieren und die letzten beiden Befehle geben jeweils `active` aus.

## Offizielle Referenzen

- [Docker Engine installieren](https://docs.docker.com/engine/install/)
- [Docker Engine auf Debian](https://docs.docker.com/engine/install/debian/)
- [Docker Compose Plugin](https://docs.docker.com/compose/install/linux/)
