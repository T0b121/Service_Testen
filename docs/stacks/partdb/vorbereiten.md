# Part-DB-Stack vorbereiten

## 1. Voraussetzungen

Vorher vollständig einrichten und prüfen:

- [Server vorbereiten](../../server/vorbereiten.md)
- [Server konfigurieren](../../server/konfigurieren.md)
- [Core-Stack: Erststart und Prüfung](../core/erststart-und-pruefung.md)
- [Core-Stack: Authentik einrichten](../core/authentik-einrichten.md)

Benötigt:

- funktionierender Core-Stack,
- funktionierendes Authentik,
- externes Docker-Netzwerk `web`,
- DNS für `partdb.<DOMAIN>`,
- vorhandene versionierte Dateien unter `Compose/partdb/`,
- OpenSSL,
- `curl` für die spätere IdP-Metadatenabfrage.

Für den normalen Betrieb wird empfohlen, den Core-Stack vorher auf öffentlich vertrauenswürdige Produktionszertifikate umzustellen. Der Aufbau ist auch mit Let's Encrypt Staging möglich; dann muss bei manuellen `curl`-Prüfungen vorübergehend `-k` verwendet werden.

## 2. Verzeichnis prüfen

```bash
cd <PROJEKT_ROOT>

find Compose/partdb -maxdepth 3 -type f -print | sort
```

Erwartet:

```text
Compose/partdb/compose.yml
Compose/partdb/config/zz-partdb.ini
Compose/partdb/scripts/partdb-entrypoint.sh
```

Das Installationsverfahren verändert diese drei versionierten Dateien nicht.

Lokales Secret-Verzeichnis anlegen:

```bash
mkdir -p Compose/partdb/secrets
chmod 700 Compose/partdb/secrets
cd Compose/partdb
```

## 3. `.env` erstellen

Für den ersten Start wird absichtlich noch kein installationsspezifisches Part-DB-Gruppenmapping vorausgesetzt. Als sichere Übergangskonfiguration wird zunächst nur der Fallback `* -> -1` gesetzt. Dadurch erhält ein neu erzeugter SAML-Benutzer durch das Mapping keine lokale Part-DB-Gruppe, bis die tatsächlichen Gruppen-IDs geprüft wurden.

Vorlage:

```dotenv
# Domain
DOMAIN=<DOMAIN>

# Docker Images Versions
PARTDB_VERSION=2.14
MARIADB_VERSION=12.3

# Part-DB
PARTDB_DEFAULT_LANG=de
PARTDB_DEFAULT_TIMEZONE=Europe/Berlin
PARTDB_BASE_CURRENCY=EUR
PARTDB_INSTANCE_NAME=Part-DB

# Database
MARIADB_DATABASE=partdb
MARIADB_USER=partdb

# SAML-Gruppenzuordnung
# Übergangswert für den ersten Start.
# Nach dem ersten lokalen Admin-Login werden die echten Part-DB-Gruppen-IDs
# ermittelt und dieser Wert ersetzt.
PARTDB_SAML_ROLE_MAPPING={"*":-1}
```

Datei erstellen:

```bash
nano .env
chmod 600 .env
```

### `DOMAIN`

Nur die Basisdomain ohne Protokoll oder Subdomain:

```dotenv
DOMAIN=<DOMAIN>
```

Nicht:

```text
https://<DOMAIN>
partdb.<DOMAIN>
```

Aus `DOMAIN` erzeugt der vorhandene Wrapper automatisch unter anderem:

```text
https://partdb.<DOMAIN>/
https://auth.<DOMAIN>/application/saml/partdb-sso/metadata/
https://partdb.<DOMAIN>/sp
```

### Image-Versionen

Getestete Versionslinien:

```dotenv
PARTDB_VERSION=2.14
MARIADB_VERSION=12.3
```

Ein Versionslinien-Tag kann bei einem bewussten `docker compose pull` eine neuere Patchversion derselben Linie laden. Vor Updates gelten die Hinweise aus [Wartung und Updates](../../wartung-und-updates.md).

### Sprache, Zeitzone und Währung

Beispiel für Deutschland:

```dotenv
PARTDB_DEFAULT_LANG=de
PARTDB_DEFAULT_TIMEZONE=Europe/Berlin
PARTDB_BASE_CURRENCY=EUR
```

`PARTDB_BASE_CURRENCY` sollte vor produktiver Datenerfassung bewusst gewählt werden. Part-DB weist darauf hin, dass die interne Basiswährung nach vorhandenen Daten nicht einfach beliebig geändert werden sollte.

### Instanzname

```dotenv
PARTDB_INSTANCE_NAME=Part-DB
```

Der Wert wird als Instanzname in Part-DB verwendet. Er ist kein Secret.

### Datenbank

```dotenv
MARIADB_DATABASE=partdb
MARIADB_USER=partdb
```

Das Datenbankpasswort gehört **nicht** in `.env`.

### `.env` prüfen

```bash
stat -c '%A %n' .env
git check-ignore -v .env
```

Erwartet:

```text
-rw------- .env
```

`git check-ignore` muss eine Regel der zentralen `.gitignore` anzeigen.

## 4. Allgemeine Secrets erzeugen

Die drei Zufallswerte werden ohne abschließenden Zeilenumbruch gespeichert, damit exakt der erzeugte Wert an Part-DB beziehungsweise MariaDB übergeben wird.

```bash
mkdir -p secrets
umask 077

openssl rand -hex 32 | tr -d '\n' > secrets/partdb_app_secret
openssl rand -hex 32 | tr -d '\n' > secrets/mariadb_password
openssl rand -hex 32 | tr -d '\n' > secrets/mariadb_root_password

chmod 600 \
  secrets/partdb_app_secret \
  secrets/mariadb_password \
  secrets/mariadb_root_password
```

`partdb_app_secret` wird als Part-DB-`APP_SECRET` verwendet. Die beiden MariaDB-Dateien enthalten das normale Datenbankpasswort und das separate Rootpasswort.

Prüfen, ohne Inhalte auszugeben:

```bash
stat -c '%A %s Bytes %n' \
  secrets/partdb_app_secret \
  secrets/mariadb_password \
  secrets/mariadb_root_password
```

Erwartet bei genau diesen Generierungsbefehlen:

```text
-rw------- 64 Bytes secrets/partdb_app_secret
-rw------- 64 Bytes secrets/mariadb_password
-rw------- 64 Bytes secrets/mariadb_root_password
```

Die Reihenfolge der Zeilen kann abweichen. Secret-Inhalte nicht mit `cat`, `echo` oder in Supportausgaben anzeigen.

## 5. SAML-SP-Schlüsselpaar erzeugen

Part-DB benötigt ein eigenes Schlüsselpaar als SAML Service Provider. Der private Schlüssel bleibt ausschließlich in `Compose/partdb/secrets/`. Authentik erhält später nur das öffentliche Zertifikat.

Domain aus der `.env` lesen:

```bash
DOMAIN_VALUE="$(sed -n 's/^DOMAIN=//p' .env | head -n1)"

if [ -z "$DOMAIN_VALUE" ]; then
  echo 'DOMAIN fehlt in .env' >&2
  exit 1
fi
```

Temporäres Arbeitsverzeichnis mit restriktiver Standardmaske:

```bash
umask 077
TMP_SAML_DIR="$(mktemp -d)"
chmod 700 "$TMP_SAML_DIR"
```

Die folgenden Schritte in derselben SSH-Sitzung ausführen. Den ausgegebenen
Pfad nicht manuell ändern. Wenn ein Schritt fehlschlägt, die temporären Dateien
erst prüfen und anschließend mit dem unten stehenden Aufräumbefehl gezielt
entfernen. Ein `trap` wird bewusst nicht verwendet: Bei einer
Schritt-für-Schritt-Ausführung oder einem Shellwechsel könnte er das
Arbeitsverzeichnis vor dem nächsten Befehl entfernen.

RSA-Schlüssel und selbstsigniertes Zertifikat erzeugen:

```bash
openssl req \
  -x509 \
  -newkey rsa:2048 \
  -sha256 \
  -nodes \
  -days 1825 \
  -subj "/CN=partdb.${DOMAIN_VALUE}/O=Part-DB SAML" \
  -keyout "$TMP_SAML_DIR/partdb-sp.key.pem" \
  -out "$TMP_SAML_DIR/partdb-sp.crt.pem"
```

Part-DB erwartet die SAML-Werte als Base64-kodierte DER-Daten ohne PEM-Kopfzeilen.

Privaten Schlüssel als PKCS#8-DER/Base64 speichern:

```bash
openssl pkcs8 \
  -topk8 \
  -nocrypt \
  -in "$TMP_SAML_DIR/partdb-sp.key.pem" \
  -outform DER \
  | base64 -w 0 \
  > secrets/partdb_saml_sp_private_key
```

Öffentliches Zertifikat als DER/Base64 speichern:

```bash
openssl x509 \
  -in "$TMP_SAML_DIR/partdb-sp.crt.pem" \
  -outform DER \
  | base64 -w 0 \
  > secrets/partdb_saml_sp_certificate
```

Rechte:

```bash
chmod 600 \
  secrets/partdb_saml_sp_private_key \
  secrets/partdb_saml_sp_certificate
```

Temporäre PEM-Dateien entfernen:

```bash
rm -rf "$TMP_SAML_DIR"
unset TMP_SAML_DIR DOMAIN_VALUE
```

## 6. SAML-SP-Zertifikat prüfen

Zertifikat lesbar?

```bash
base64 -d secrets/partdb_saml_sp_certificate \
  | openssl x509 -inform DER -noout \
      -subject \
      -issuer \
      -dates \
      -fingerprint -sha256
```

Erwartet:

- Subject enthält `CN=partdb.<DOMAIN>`.
- Das Zertifikat ist selbstsigniert, daher sind Subject und Issuer identisch beziehungsweise enthalten dieselbe Identität.
- Gültigkeit liegt ungefähr fünf Jahre in der Zukunft.

Öffentliche Schlüssel von Zertifikat und Private Key vergleichen:

```bash
CERT_PUB_SHA="$({
  base64 -d secrets/partdb_saml_sp_certificate \
    | openssl x509 -inform DER -pubkey -noout \
    | openssl pkey -pubin -outform DER 2>/dev/null
} | sha256sum | awk '{print $1}')"

KEY_PUB_SHA="$({
  base64 -d secrets/partdb_saml_sp_private_key \
    | openssl pkey -inform DER -pubout -outform DER 2>/dev/null
} | sha256sum | awk '{print $1}')"

printf 'Zertifikat: %s\nPrivate Key: %s\n' \
  "$CERT_PUB_SHA" \
  "$KEY_PUB_SHA"
```

Beide SHA-256-Werte müssen identisch sein.

```bash
unset CERT_PUB_SHA KEY_PUB_SHA
```

## 7. Fehlendes IdP-Zertifikat ist zu diesem Zeitpunkt normal

Die Datei:

```text
secrets/authentik_saml_idp_certificate
```

wird erst erzeugt, nachdem in Authentik der SAML-Provider `Part-DB SSO` eingerichtet wurde. Dessen Metadata-Endpunkt enthält das tatsächlich verwendete Authentik-Signing-Zertifikat.

Deshalb **jetzt noch nicht** `docker compose up -d` ausführen.

Als nächstes folgt:

- [Authentik für Part-DB einrichten](authentik-einrichten.md)

Dort wird am Ende auch `secrets/authentik_saml_idp_certificate` erzeugt.

## 8. Git-Schutz prüfen

```bash
cd <PROJEKT_ROOT>

git check-ignore -v \
  Compose/partdb/.env \
  Compose/partdb/secrets/partdb_app_secret \
  Compose/partdb/secrets/mariadb_password \
  Compose/partdb/secrets/mariadb_root_password \
  Compose/partdb/secrets/partdb_saml_sp_certificate \
  Compose/partdb/secrets/partdb_saml_sp_private_key
```

Jeder Pfad muss durch die zentrale `.gitignore` erfasst werden.

## 9. DNS prüfen

```bash
getent ahostsv4 partdb.<DOMAIN>
```

Erwartet: die öffentliche IPv4-Adresse des Servers.

Bei bewusst verwendetem IPv6 zusätzlich:

```bash
getent ahostsv6 partdb.<DOMAIN>
```

Ein AAAA-Eintrag darf nur existieren, wenn der Server über IPv6 tatsächlich auf TCP 80 und 443 erreichbar ist.

## 10. Core und Netzwerk prüfen

```bash
docker network inspect web >/dev/null

cd <PROJEKT_ROOT>/Compose/core
docker compose ps
```

Core muss laufen und gesund sein. Der Part-DB-Outpost-Router wird erst mit dem Part-DB-Container registriert und nach dem Start geprüft.

## 11. Keine zusätzlichen Part-DB-Variablen blind in `.env` schreiben

Docker Compose verwendet `.env` zunächst zur Variablenersetzung. Eine Variable wird **nicht automatisch** in den Part-DB-Container weitergereicht, nur weil sie in `.env` steht.

Der aktuelle Stack übergibt bewusst nur die Variablen, die in `compose.yml` und `scripts/partdb-entrypoint.sh` vorgesehen sind.

Folge:

- normale Part-DB-Einstellungen bevorzugt über die Part-DB-Weboberfläche konfigurieren,
- Provider-API-Schlüssel über die Weboberfläche konfigurieren, wenn Part-DB diese Einstellung dort anbietet,
- nicht davon ausgehen, dass ein zusätzliches `PROVIDER_*=` oder anderes env-only Setting in `.env` automatisch wirksam wird,
- für eine künftig benötigte env-only Funktion eine bewusste, versionierte Erweiterung des Stackdesigns vornehmen, statt auf einem einzelnen Server `compose.yml` manuell abzuändern.

Damit bleibt die Installation reproduzierbar.

## 12. Zwischenstand

Vor dem Authentik-Schritt müssen vorhanden sein:

```text
Compose/partdb/.env
Compose/partdb/secrets/partdb_app_secret
Compose/partdb/secrets/mariadb_password
Compose/partdb/secrets/mariadb_root_password
Compose/partdb/secrets/partdb_saml_sp_certificate
Compose/partdb/secrets/partdb_saml_sp_private_key
```

Noch nicht vorhanden:

```text
Compose/partdb/secrets/authentik_saml_idp_certificate
```

Das ist an dieser Stelle korrekt.

## Offizielle Referenzen

- [Part-DB: Docker-Installation](https://docs.part-db.de/installation/installation_docker.html)
- [Part-DB: Konfiguration](https://docs.part-db.de/configuration.html)
- [Part-DB: Reverse Proxy](https://docs.part-db.de/installation/reverse-proxy.html)
- [Part-DB: SAML SSO](https://docs.part-db.de/installation/saml_sso.html)
