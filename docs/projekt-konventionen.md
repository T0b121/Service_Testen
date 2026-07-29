# Projektkonventionen

Diese Regeln gelten stackübergreifend. Stack-spezifische Dienste, Ports, Netzwerke, Secrets und Umgebungsvariablen werden dagegen ausschließlich unter `docs/stacks/<stack-name>/` dokumentiert.

## 1. Verzeichnisstruktur

Ein Stack kann neben `compose.yml` zusätzliche **versionierte** Hilfsdateien besitzen. Installationsabhängige Dateien bleiben dagegen lokal.

```text
<PROJEKT_ROOT>/
├── README.md
├── .gitignore
├── Compose/
│   └── <stack-name>/
│       ├── compose.yml              # versioniert
│       ├── config/                  # optional, versioniert
│       ├── scripts/                 # optional, versioniert
│       ├── .env                     # lokal, nicht versioniert
│       └── secrets/                 # lokal, nicht versioniert
└── docs/
    ├── ...
    └── stacks/
        └── <stack-name>/
```

Regeln:

- Platzhalter wie `<PROJEKT_ROOT>`, `<DOMAIN>` oder `<EMPFAENGER_EMAIL>` werden vor der Ausführung ersetzt. Die spitzen Klammern werden nicht mitkopiert.
- Ein Stack liegt unter `Compose/<stack-name>/`.
- Die zugehörige Dokumentation liegt unter `docs/stacks/<stack-name>/`.
- Der Compose-Dateiname lautet einheitlich `compose.yml`.
- Dateinamen der Dokumentation verwenden Kleinbuchstaben und Bindestriche.
- `<PROJEKT_ROOT>` ist das Root-Verzeichnis des Git-Repositorys und kein fest vorgegebener Betriebssystempfad.
- `config/` und `scripts/` enthalten nur wiederverwendbare, installationsunabhängige Dateien.
- `.env`, `secrets/`, lokal erzeugte Zertifikate und private Schlüssel werden nicht versioniert.

## 2. Installationsprinzip: versionierte Docker-Dateien nicht lokal bearbeiten

Eine normale Installation wird durch **lokale Eingabedaten** konfiguriert, nicht durch Handänderungen an den versionierten Docker-Dateien.

Die vorgesehenen Eingabestellen sind:

- `.env` für nicht geheime installationsabhängige Werte,
- `secrets/` für Passwörter, Schlüssel und andere lokale Secret-Dateien,
- Verwaltungsoberflächen beziehungsweise APIs der Anwendungen für anwendungseigene Konfiguration.

`compose.yml`, versionierte Dateien unter `config/` und versionierte Skripte unter `scripts/` bleiben auf allen Installationen gleich. Dadurch kann derselbe Git-Stand mit unterschiedlichen Basisdomains und lokalen Secrets verwendet werden.

Eine Änderung an diesen versionierten Dateien ist eine **Änderung des Stackdesigns**. Sie wird im Repository vorgenommen und dokumentiert, nicht einmalig auf einem einzelnen Server.

Projektweite feste Konventionen dürfen in versionierten Dateien vorkommen. Konkrete Subdomains, Namen und Kennungen werden beim jeweiligen Stack dokumentiert; die Basisdomain wird weiterhin nur über `DOMAIN` gewählt.

## 3. Mindestdokumentation pro Stack

Jeder Stack erhält mindestens:

```text
uebersicht.md
vorbereiten.md
erststart-und-pruefung.md
betrieb.md
backup-und-wiederherstellung.md
fehlerbehebung.md
```

Zusätzliche Oberflächen- oder Anwendungsanleitungen werden als eigene Dateien ergänzt.

Die Stack-Dokumentation muss mindestens enthalten:

- enthaltene Dienste und deren Zweck
- öffentliche und interne Erreichbarkeit
- vorausgesetzte Stacks
- benötigte Netzwerke
- persistente Volumes
- benötigte `.env`-Werte
- benötigte Secrets
- Erstellung aller Passwörter, Schlüssel und Tokens
- Erststart
- Healthchecks beziehungsweise ausdrücklich, wenn ein Dienst keinen Docker-Healthcheck besitzt
- Logbefehle
- normaler Betrieb
- Backup-Inventar
- Wiederherstellungsreihenfolge
- typische Fehler

## 4. `.env`

Die echte `.env`:

- liegt direkt beim jeweiligen `compose.yml`,
- wird nicht in Git eingecheckt,
- enthält keine Passwörter, sofern der Dienst Datei-Secrets unterstützt,
- erhält Dateimodus `600`,
- wird in der Stack-Dokumentation vollständig als kommentierte Vorlage gezeigt.

Eine physische `.env.example` ist in diesem Projekt nicht erforderlich. Die Vorlage wird in `vorbereiten.md` gepflegt, damit Herkunft und Zweck jedes Werts direkt erläutert werden.

Wichtig: Docker Compose verwendet `.env` zunächst für die **Variablenersetzung**. Eine zusätzliche Variable wird nicht automatisch in einen Container injiziert, nur weil sie in `.env` steht. Sie muss in `compose.yml`, einem `env_file` oder einem dafür vorgesehenen Wrapper tatsächlich an den Dienst weitergegeben werden.

Daraus folgt für dieses Projekt: Neue env-only Funktionen werden nicht durch beliebige zusätzliche Zeilen in `.env` und nicht durch lokale Compose-Handänderungen „aktiviert“. Wenn eine solche Funktion benötigt wird, wird die Weitergabe reproduzierbar im versionierten Stackdesign ergänzt.

Prüfung:

```bash
chmod 600 .env
stat -c '%A %n' .env
git check-ignore -v .env
```

Erwartet:

- `stat` beginnt mit `-rw-------`.
- `git check-ignore` gibt die passende Regel aus `.gitignore` aus.
- Keine Ausgabe von `git check-ignore` bedeutet, dass die Datei nicht ignoriert wird.

## 5. Secrets

Secrets liegen unter:

```text
Compose/<stack-name>/secrets/
```

Regeln:

- Das Verzeichnis wird vollständig von Git ignoriert.
- Secret-Dateien erhalten Modus `600`.
- Secret-Inhalte werden nicht mit `cat`, `echo` oder ähnlichen Befehlen auf Terminal beziehungsweise in Logs ausgegeben. Internes Einlesen mit direkter Umleitung in eine geschützte Datei ist davon zu unterscheiden.
- Jedes Secret wird nur den Diensten zugeordnet, die es tatsächlich benötigen.
- Die Erzeugung jedes Secrets wird in der Stack-Dokumentation beschrieben.
- Secret-Dateien werden verschlüsselt gesichert.

Bei lokalem Docker Compose werden dateibasierte Secrets im Container unter `/run/secrets/<name>` eingehängt. Auf dem Host bleiben die Quelldateien normale Klartextdateien. Compose-Secrets verhindern daher nicht den Zugriff eines privilegierten Host-Benutzers und ersetzen keinen verschlüsselten Secret-Manager.

## 6. Passwörter, Schlüssel, Hashes und Kodierungen

Diese Begriffe sind nicht austauschbar:

- **Zufallswert/Secret:** muss mit einem kryptografisch sicheren Zufallsgenerator erzeugt werden.
- **Passwort:** kann zufällig erzeugt oder in einem Passwortmanager generiert werden.
- **Hash:** dient hier meist der Integritätsprüfung; er verschlüsselt keine Daten.
- **Base64:** ist nur eine Kodierung und keine Verschlüsselung.
- **Base64url:** URL-taugliche Base64-Variante; ebenfalls keine Verschlüsselung.
- **Provider-Secret:** wird von einem externen Dienst ausgegeben und darf nicht selbst erfunden werden.

### Zufälliges Secret als Base64

```bash
umask 077
openssl rand -base64 32 | tr -d '\n' > secret_datei
```

### Zufälliges Secret als Hex

```bash
umask 077
openssl rand -hex 32 > secret_datei
```

### Zufälliges URL-taugliches Token

Nur verwenden, wenn die Zielanwendung ausdrücklich ein selbst erzeugtes Base64url-Token erwartet:

```bash
umask 077
openssl rand -base64 32 \
  | tr '+/' '-_' \
  | tr -d '=\n' \
  > secret_datei
```

### Bestehenden Text Base64-kodieren

```bash
printf '%s' 'ZU_KODIERENDER_TEXT' | base64 -w 0
```

Rückumwandlung:

```bash
printf '%s' 'BASE64_WERT' | base64 -d
```

Base64 schützt den Inhalt nicht.

### SHA-256-Prüfsumme erstellen

```bash
sha256sum DATEI > DATEI.sha256
```

Prüfen:

```bash
sha256sum -c DATEI.sha256
```

Ein Hash weist Veränderungen nach, ersetzt aber weder Signatur noch Verschlüsselung.

### Werte externer Anbieter

Werte wie OAuth-Client-Secrets, App-Passwörter, API-Tokens sowie ACME-EAB-Werte werden normalerweise durch den jeweiligen Anbieter erzeugt. Sie werden nicht mit `openssl rand` ersetzt.

Insbesondere:

- `eab.kid`: vom ACME-Anbieter vergebene Kennung
- `eab.hmacEncoded`: vom ACME-Anbieter ausgegebener HMAC-Schlüssel in der verlangten Kodierung

## 7. Image-Versionen

Es wird kein `latest` verwendet.

Beispiel:

```dotenv
TRAEFIK_VERSION=3.7
```

Ein Versionslinien-Tag wie `3.7` kann bei `docker compose pull` eine neuere `3.7.x`-Version laden. Das ist beabsichtigt, damit Patch- und Sicherheitskorrekturen innerhalb der gewählten Linie kontrolliert übernommen werden können.

Unterschiede:

| Form | Beispiel | Verhalten |
|---|---|---|
| Versionslinie | `3.7` | neueste verfügbare Patchversion dieser Linie |
| vollständiger Tag | `3.7.9` | festgelegte Patchversion |
| Digest | `image@sha256:...` | unveränderbares Image |

Vor jeder Aktualisierung werden Release Notes, Backups und Rollback-Möglichkeit geprüft.

## 8. Netzwerke und Ports

- Nur tatsächlich öffentliche Dienste erhalten `ports:`.
- Interne Dienste verwenden Docker-Netzwerke und gegebenenfalls `expose:`.
- Ein gemeinsames externes Proxy-Netzwerk heißt `web`.
- Interne Stack-Netzwerke erhalten einen stackbezogenen Namen, beispielsweise `core_auth`.
- Ein `internal: true`-Netzwerk verhindert regulären externen Egress aus diesem Netzwerk.
- Ein Dienst wird nur an Netzwerke angeschlossen, die er benötigt.

`expose:` veröffentlicht keinen Port am Host.

## 9. Volumes

Persistente Daten werden in benannten Volumes gespeichert.

Namensschema:

```text
<stack>_<dienst-oder-zweck>
```

Beispiele:

```text
<stack>_<dienst>_data
```

Jeder Stack dokumentiert:

- welches Volume welche Daten enthält,
- ob ein konsistenter Anwendungsdump erforderlich ist,
- ob der Dienst vor einer Volume-Sicherung gestoppt werden muss,
- in welcher Reihenfolge wiederhergestellt wird.

## 10. Startabhängigkeiten

Die zentrale `README.md` nennt für jeden Stack die **vorausgesetzten Stacks**.

Vor dem Start eines Stacks müssen dessen vorausgesetzte Stacks laufen und gesund sein. Innerhalb eines Compose-Stacks werden Dienstabhängigkeiten über `depends_on` und Healthchecks abgebildet, soweit dies technisch sinnvoll ist.

## 11. Standardbefehle

Alle Befehle werden im jeweiligen Stack-Verzeichnis ausgeführt:

```bash
cd <PROJEKT_ROOT>/Compose/<stack-name>
```

Konfiguration prüfen:

```bash
docker compose config --quiet
```

Erwartet: keine Ausgabe und Exit-Code `0`. Eine Fehlermeldung muss vor dem Start behoben werden.

Aufgelöste Konfiguration ansehen:

```bash
docker compose config
```

Starten:

```bash
docker compose up -d
```

Status:

```bash
docker compose ps
```

Logs:

```bash
docker compose logs --tail=100
docker compose logs -f
docker compose logs --since=15m <dienst>
```

Stoppen und starten:

```bash
docker compose stop
docker compose start
```

Container entfernen, Daten behalten:

```bash
docker compose down
```

`docker compose down -v` wird nur bei ausdrücklich beabsichtigter Datenlöschung verwendet.

## 12. Log-Rotation

Jeder dauerhafte Dienst erhält eine begrenzte Docker-Loggröße, beispielsweise:

```yaml
logging:
  driver: json-file
  options:
    max-size: 10m
    max-file: "3"
```

Das verhindert unbegrenzt wachsende JSON-Logs. Anwendungsinterne Logs und Datenbanken müssen zusätzlich separat betrachtet werden.

## 13. Backups

Jeder Stack besitzt eine eigene Backup-Datei. Die allgemeine Strategie steht in [Backup und Wiederherstellung](backup-und-wiederherstellung.md).

Mindestens zu berücksichtigen:

- `compose.yml`
- lokale `.env`
- Secret-Dateien
- Datenbankdumps
- persistente Anwendungsdaten
- Zertifikats- oder ACME-Daten
- Prüfsummen
- Wiederherstellungstest

## Offizielle Referenzen

- [Docker Compose Secrets](https://docs.docker.com/compose/how-tos/use-secrets/)
- [Docker Compose Services](https://docs.docker.com/reference/compose-file/services/)
- [Docker Port Publishing](https://docs.docker.com/engine/network/port-publishing/)
