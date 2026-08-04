# TLS und Zertifikate

Dieses Dokument beschreibt die gemeinsame TLS- und ACME-Strategie. Let’s Encrypt ist der Standard. Andere ACME-Anbieter sind nur als Zusatzinformation dokumentiert.

## 1. Begriffe

- **TLS:** verschlüsselt die Verbindung zwischen Client und Server.
- **Zertifikat:** bindet einen öffentlichen Schlüssel an einen Domainnamen.
- **ACME:** Protokoll zur automatischen Ausstellung und Erneuerung von Zertifikaten.
- **Certificate Resolver:** Traefik-Konfiguration, die ACME-Konto, Challenge und Speicher verwaltet.
- **Staging:** Testumgebung mit nicht öffentlich vertrauenswürdigen Zertifikaten.
- **Produktion:** Umgebung für öffentlich vertrauenswürdige Zertifikate.

## 2. Verwendete Challenge: HTTP-01

Der Core-Stack verwendet HTTP-01:

```yaml
- --certificatesresolvers.letsencrypt.acme.httpchallenge=true
- --certificatesresolvers.letsencrypt.acme.httpchallenge.entrypoint=web
```

Voraussetzungen:

- Der Domainname zeigt auf den Server.
- TCP 80 ist aus dem Internet erreichbar.
- Traefik veröffentlicht Port 80.
- Kein anderer Dienst belegt Port 80.
- Ein vorhandener AAAA-Eintrag muss ebenfalls korrekt erreichbar sein.
- Die ACME-Challenge darf nicht durch eine vorgeschaltete Firewall oder einen fremden Proxy blockiert werden.

Wildcard-Zertifikate können nicht über HTTP-01 bezogen werden. Dafür wäre DNS-01 erforderlich.

## 3. Resolver und Router-Labels

Router wählen den Resolver nur über seinen Namen:

```yaml
- traefik.http.routers.authentik.tls.certresolver=letsencrypt
- traefik.http.routers.traefik-dashboard.tls.certresolver=letsencrypt
```

Alle öffentlichen Router teilen die zentrale ACME-Konfiguration von Traefik.

Diese Labels werden beim Wechsel zwischen Staging und Produktion **nicht geändert**.

Der aktive ACME-Server und das verwendete Volume kommen aus `.env`:

```yaml
- --certificatesresolvers.letsencrypt.acme.caserver=${ACME_CA_SERVER}
```

```yaml
volumes:
  traefik_acme:
    name: ${TRAEFIK_ACME_VOLUME}
```

## 4. Let’s Encrypt Staging

Staging wird verwendet:

- beim ersten Aufbau,
- nach grundlegenden Änderungen an DNS oder Routing,
- beim Test einer neuen Installation,
- solange Authentik, Outpost und Dashboard nicht vollständig geprüft wurden,
- zur Diagnose wiederholter ACME-Fehler.

Aktive `.env`-Werte:

```dotenv
ACME_CA_SERVER=https://acme-staging-v02.api.letsencrypt.org/directory
TRAEFIK_ACME_VOLUME=core_traefik_acme_staging
```

Eigenschaften:

- Zertifikate sind nicht öffentlich vertrauenswürdig.
- Browserwarnungen sind erwartbar.
- Staging besitzt ein eigenes ACME-Konto.
- Staging und Produktion verwenden getrennte Volumes.

## 5. Voraussetzungen vor Produktion

Der Produktionswechsel wird im **Core-Stack** durchgeführt, weil dort Traefik und der ACME-Resolver konfiguriert sind. Die versionierten Router-Labels werden dabei nicht geändert.

Vor dem Wechsel müssen mindestens die Core-Prüfungen erfolgreich sein:

- DNS-A-Einträge für die bereits eingerichteten öffentlichen Dienste stimmen.
- Vorhandene AAAA-Einträge stimmen und IPv6 ist erreichbar.
- TCP 80 und 443 sind öffentlich erreichbar.
- HTTP wird auf HTTPS weitergeleitet.
- Traefik ist `healthy`.
- Authentik Server, Worker und PostgreSQL sind `healthy`.
- `https://auth.<DOMAIN>` funktioniert.
- der Authentik-Outpost-Ping liefert `204`.
- das Traefik-Dashboard funktioniert nach Authentik-Anmeldung.
- der Dashboard-Callback endet nicht mit `404`.
- Zugriff für Nicht-Administratoren wurde negativ getestet.
- Traefik-Logs enthalten keine ungelösten ACME-Fehler.

Bei bereits eingerichteten zusätzlichen Stacks außerdem die in deren Betriebsdokumentation vorgesehenen Erreichbarkeits- und Zugriffstests ausführen.

## 6. Von Staging auf Produktion wechseln

Im Stack-Verzeichnis:

```bash
cd <PROJEKT_ROOT>/Compose/core
```

In `.env` die beiden aktiven Staging-Zeilen auskommentieren:

```dotenv
# ACME_CA_SERVER=https://acme-staging-v02.api.letsencrypt.org/directory
# TRAEFIK_ACME_VOLUME=core_traefik_acme_staging
```

Die Produktionszeilen aktivieren:

```dotenv
ACME_CA_SERVER=https://acme-v02.api.letsencrypt.org/directory
TRAEFIK_ACME_VOLUME=core_traefik_acme_production
```

Danach:

```bash
docker compose config --quiet
```

Aufgelöste Werte kontrollieren:

```bash
docker compose config \
  | grep -E 'acme\.(storage|caserver)'
```

Volume kontrollieren:

```bash
docker compose config \
  | grep -A3 'traefik_acme:'
```

Erwartet:

```text
acme.caserver=https://acme-v02.api.letsencrypt.org/directory
name: core_traefik_acme_production
```

Nur Traefik neu erstellen:

```bash
docker compose up -d --force-recreate traefik
```

Status und Logs:

```bash
docker compose ps
docker compose logs --tail=150 traefik
```

Das Produktionsvolume wird beim ersten Start automatisch angelegt. Das Staging-Volume bleibt getrennt erhalten.

Die zusätzlichen Stacks Part-DB, Ollama, Open WebUI, LiteLLM, SearXNG und Jellyfin benötigen
dabei keine Änderung an ihrer `compose.yml` oder `.env`. Ihre Router verweisen
bereits auf den Resolvernamen `letsencrypt`; dessen Staging-/Produktionsziel
wird zentral im Core-Stack bestimmt.

## 7. Warum getrennte Volumes?

Traefik speichert in `/acme/acme.json` unter anderem:

- ACME-Kontodaten,
- private Schlüssel,
- ausgestellte Zertifikate,
- Erneuerungsinformationen.

Staging und Produktion verwenden unterschiedliche ACME-Konten und Zertifikatsketten. Deshalb werden getrennte Volumes benutzt:

```text
core_traefik_acme_staging
core_traefik_acme_production
```

Staging-Daten werden nicht in das Produktionsvolume kopiert.

## 8. Zertifikate kontrollieren

Für jeden öffentlichen Host kann dasselbe Prüfmuster verwendet werden.

Authentik:

```bash
openssl s_client \
  -connect auth.<DOMAIN>:443 \
  -servername auth.<DOMAIN> \
  </dev/null 2>/dev/null \
  | openssl x509 -noout \
      -subject \
      -issuer \
      -dates \
      -serial
```

Traefik-Dashboard:

```bash
openssl s_client \
  -connect proxy.<DOMAIN>:443 \
  -servername proxy.<DOMAIN> \
  </dev/null 2>/dev/null \
  | openssl x509 -noout -subject -issuer -dates
```

Weitere öffentliche Dienste gemäß [Dienste-Übersicht](dienste.md):

```bash
openssl s_client \
  -connect <HOSTNAME>:443 \
  -servername <HOSTNAME> \
  </dev/null 2>/dev/null \
  | openssl x509 -noout -subject -issuer -dates
```

`<HOSTNAME>` ist dabei nur der DNS-Name ohne `https://` und ohne Pfad.

Zusätzlich im Browser beziehungsweise Client prüfen:

- Domainname,
- Aussteller,
- Gültigkeitszeitraum,
- keine Staging-Warnung im Produktivbetrieb,
- vollständige Zertifikatskette.

Öffentlich vertrauenswürdige Zertifikate sind besonders wichtig für Maschinenclients wie KiCad, die Staging- oder selbstsignierten Zertifikaten nicht automatisch vertrauen.

## 9. Automatische Erneuerung

Traefik verwaltet die Erneuerung selbst. Voraussetzungen:

- Traefik läuft regelmäßig.
- DNS zeigt weiterhin auf den Server.
- der verwendete Challenge-Port bleibt erreichbar.
- das ACME-Volume bleibt persistent und beschreibbar.
- Systemzeit und DNS funktionieren.

Logs prüfen:

```bash
docker compose logs traefik \
  | grep -Ei 'acme|certificate|renew|challenge|error'
```

Das Löschen des Produktionsvolumes erzwingt eine Neuregistrierung und Neuausstellung. Das kann Rate-Limits auslösen und ist kein normaler Erneuerungsschritt.

## 10. Zurück zu Staging

Zur Diagnose können die Produktionswerte wieder auskommentiert und die Staging-Werte aktiviert werden. Danach wird Traefik erneut erstellt.

Die beiden Werte werden immer gemeinsam geändert:

```text
ACME_CA_SERVER
TRAEFIK_ACME_VOLUME
```

Nie den Produktionsserver mit dem Staging-Volume oder umgekehrt kombinieren.

## 11. Rate-Limits und Fehlervermeidung

- Neue Installationen zuerst gegen Staging testen.
- Produktionsvolume nicht unnötig löschen.
- Router nicht wiederholt mit wechselnden Domainnamen neu erstellen.
- Fehlerhafte AAAA-Einträge entfernen oder korrigieren.
- Zertifikate nicht manuell in kurzen Abständen neu anfordern.
- Vor Änderungen Backup des Produktions-ACME-Volumes erstellen.

## 12. Alternative ACME-Anbieter

Let’s Encrypt bleibt die Standardkonfiguration. Alternativen sind nur sinnvoll, wenn dafür ein konkreter betrieblicher Grund besteht.

Die aktuell versionierte Core-Konfiguration macht bei einer normalen Installation nur `ACME_CA_SERVER` und `TRAEFIK_ACME_VOLUME` über `.env` variabel. Zusätzliche ACME-Funktionen wie External Account Binding (EAB) sind **nicht** in `Compose/core/compose.yml` verdrahtet. Ein EAB-Anbieter erfordert deshalb zuerst eine bewusst versionierte Erweiterung des Stackdesigns. Es reicht nicht, EAB-Werte nur in `.env` einzutragen, und die `compose.yml` soll nicht installationsspezifisch lokal editiert werden.

Traefik selbst unterstützt External Account Binding:

```yaml
- --certificatesresolvers.<resolver>.acme.eab.kid=<EAB_KID>
- --certificatesresolvers.<resolver>.acme.eab.hmacencoded=<EAB_HMAC_ENCODED>
```

### Bedeutung der EAB-Werte

- `eab.kid`: Kennung des vom Anbieter ausgegebenen EAB-Schlüssels.
- `eab.hmacEncoded`: vom Anbieter ausgegebener HMAC-Schlüssel; Traefik erwartet Base64url ohne Padding.
- Diese Werte werden durch den Anbieter erzeugt.
- Sie werden nicht durch ein zufälliges lokales Passwort ersetzt.
- Vor einer erneuten Kodierung ist die Dokumentation des Anbieters zu prüfen. Häufig wird bereits das korrekte Format geliefert.
- Der HMAC-Wert ist ein Secret.
- Base64url ist nur die Übertragungsform und keine Verschlüsselung.

### ZeroSSL

ACME-Verzeichnis:

```text
https://acme.zerossl.com/v2/DV90
```

Zu beachten:

- ZeroSSL-Konto erforderlich.
- EAB-Zugangsdaten werden im Developer-Bereich oder über die ZeroSSL-API erzeugt.
- `kid` und HMAC gehören zum ZeroSSL-Konto.
- Der HMAC darf nicht in Git eingecheckt werden.
- Vor produktiver Nutzung aktuelle Kontingente und Tarifbedingungen prüfen.

### Google Trust Services / Public CA

Produktionsverzeichnis:

```text
https://dv.acme-v02.api.pki.goog/directory
```

Staging-Verzeichnis:

```text
https://dv.acme-v02.test-api.pki.goog/directory
```

EAB-Schlüssel werden über Google Cloud erzeugt:

```bash
gcloud publicca external-account-keys create
```

Die Ausgabe enthält:

- `keyId` → `eab.kid`
- `b64MacKey` → `eab.hmacEncoded`

Zu beachten:

- Google-Cloud-Projekt erforderlich.
- Das EAB-Secret muss laut Anbieter innerhalb des vorgegebenen Zeitfensters verwendet werden.
- Ein EAB-Secret registriert nur ein ACME-Konto und ist anschließend nicht wiederverwendbar.
- `b64MacKey` ist bereits Base64url-kodiert.

### Sichere Ablage von EAB-Werten

Die Default-Konfiguration verwendet keine EAB-Werte. Bei einer späteren, **versionierten** Erweiterung gilt:

- HMAC niemals direkt in `compose.yml` eintragen.
- nur Variablen oder Secret-Pfade verwenden, die die versionierte Stackkonfiguration ausdrücklich an Traefik weitergibt; ein zusätzlicher Eintrag in `.env` alleine hat keine Wirkung.
- lokale `.env` mindestens mit Modus `600` schützen und durch Git ignorieren, sofern das gewählte Design dort nicht geheime EAB-Metadaten ablegt.
- für den HMAC bevorzugt einen Datei-Secret- oder geeigneten Secret-Manager-Ansatz verwenden.
- den EAB-Wert nicht in Logs oder Supportausgaben kopieren.

## Offizielle Referenzen

- [Let’s Encrypt Staging](https://letsencrypt.org/docs/staging-environment/)
- [Let’s Encrypt ACME-Endpunkte](https://letsencrypt.org/docs/acme-protocol-updates/)
- [Traefik ACME Resolver](https://doc.traefik.io/traefik/reference/install-configuration/tls/certificate-resolvers/acme/)
- [ZeroSSL ACME](https://zerossl.com/documentation/acme/)
- [Google Public CA mit ACME](https://cloud.google.com/certificate-manager/docs/public-ca-tutorial)
