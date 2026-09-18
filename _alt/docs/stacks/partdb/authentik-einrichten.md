# Part-DB-Stack: Authentik einrichten

Dieses Dokument wird nach [vorbereiten.md](vorbereiten.md) und **vor dem ersten Part-DB-Start** durchgeführt.

Ziel ist eine zweistufige Authentifizierung:

1. `Part-DB Access` als äußerer Forward-Auth-Schutz,
2. `Part-DB SSO` als nativer SAML-Provider für die Anmeldung in Part-DB.

Die hier beschriebenen Namen und Slugs sind Teil der getesteten Projektkonfiguration. Insbesondere der Slug `partdb-sso` muss unverändert bleiben, weil der Part-DB-Entrypoint daraus die IdP-Endpunkte ableitet.

Part-DB führt SAML derzeit als **Beta-Funktion**. Authentik ist ein SAML-2.0-Identity-Provider und die hier beschriebene Konfiguration wurde mit diesem Projekt getestet; nach Versionswechseln müssen SAML-Login, Logout, Signaturprüfung und Gruppenmapping erneut kontrolliert werden.

## 1. Authentik-Gruppen anlegen

Navigation:

```text
Directory → Groups
```

Folgende Gruppen anlegen:

```text
partdb-admin
partdb-editor
partdb-readonly
```

Zweck:

| Authentik-Gruppe | Bedeutung |
|---|---|
| `partdb-admin` | administrativer Zugang zu Part-DB |
| `partdb-editor` | normaler schreibender Benutzer |
| `partdb-readonly` | lesender Benutzer |

Für die erste Einrichtung den Authentik-Administrator beziehungsweise das verwendete Administratorkonto mindestens `partdb-admin` zuordnen.

Noch keine Part-DB-Gruppen-IDs eintragen. Diese existieren installationsspezifisch und werden erst nach dem ersten Part-DB-Start geprüft.

## 2. Öffentliches Part-DB-SP-Zertifikat für Authentik vorbereiten

Auf dem Server:

```bash
cd <PROJEKT_ROOT>/Compose/partdb

base64 -d secrets/partdb_saml_sp_certificate \
  | openssl x509 -inform DER -outform PEM \
  > /tmp/partdb-saml-sp-certificate.pem

chmod 600 /tmp/partdb-saml-sp-certificate.pem
```

Die Datei enthält ausschließlich das **öffentliche** Zertifikat. Der private Schlüssel aus `secrets/partdb_saml_sp_private_key` wird niemals in Authentik importiert.

## 3. Part-DB-SP-Zertifikat in Authentik importieren

Navigation:

```text
System → Certificates
```

Neues Zertifikat importieren:

```text
Name: Part-DB SAML SP
Certificate: Inhalt von /tmp/partdb-saml-sp-certificate.pem
Private Key: leer
```

Speichern und kontrollieren:

```text
Name: Part-DB SAML SP
Private key: No / Nein
```

Danach die temporäre Datei auf dem Server entfernen:

```bash
rm -f /tmp/partdb-saml-sp-certificate.pem
```

## 4. Äußere Anwendung `Part-DB Access` anlegen

Navigation:

```text
Applications → Applications
```

Neue Anwendung mit Proxy Provider erstellen.

### Anwendung

```text
Name: Part-DB Access
Slug: partdb-access
Group: Part-DB
Policy Engine Mode: ANY
Launch URL: https://partdb.<DOMAIN>/
```

### Proxy Provider

```text
Name: Part-DB Access
Type: Proxy Provider
Authorization Flow: default-provider-authorization-implicit-consent
Mode: Forward auth (single application)
External host: https://partdb.<DOMAIN>
```

Keine unauthentifizierten Pfade eintragen.

Der Single-Application-Modus ist hier absichtlich gewählt: Part-DB erhält eine eigene Anwendung und eigene Bindings. Authentik dokumentiert für diesen Modus, dass die Anwendung selbst weiter durch Traefik bedient wird und nur `/outpost.goauthentik.io/` zur Authentik-Outpost-Route gehen muss. Diese Route wird beim Start des Part-DB-Stacks bereitgestellt.

## 5. Bindings für `Part-DB Access`

An der Anwendung die Gruppenbindungen anlegen:

| Gruppe | Order | Enabled | Negate | Timeout | Failure result |
|---|---:|---|---|---:|---|
| `partdb-admin` | 0 | Ja | Nein | 30 | fail |
| `partdb-editor` | 10 | Ja | Nein | 30 | fail |
| `partdb-readonly` | 20 | Ja | Nein | 30 | fail |

Mit `Policy Engine Mode: ANY` reicht eine der zulässigen Gruppen.

Damit erhalten nur Benutzer aus mindestens einer dieser Gruppen Zugang durch die äußere Schutzschicht.

## 6. `Part-DB Access` dem Embedded Outpost zuordnen

Navigation:

```text
Applications → Outposts
→ authentik Embedded Outpost
→ Edit
```

Unter Anwendungen `Part-DB Access` zu den ausgewählten Anwendungen verschieben und speichern.

Danach sollte der zugehörige Proxy Provider im Embedded Outpost erscheinen.

## 7. SAML-Gruppen-Property-Mapping anlegen

Part-DB erwartet Gruppen beziehungsweise Rollen im SAML-Attribut:

```text
group
```

Navigation:

```text
Customization → Property Mappings
```

Neue **SAML Provider Property Mapping** anlegen:

```text
Name: Part-DB Gruppen
SAML Attribute Name: group
```

Expression:

```python
for group in user.groups.all():
    if group.name in [
        "partdb-admin",
        "partdb-editor",
        "partdb-readonly",
    ]:
        yield group.name
```

Nur die drei vorgesehenen Part-DB-Gruppen werden übertragen.

Falls die Oberfläche einen Mapping-Test anbietet, mindestens prüfen:

```text
Benutzer in partdb-admin     → ["partdb-admin"]
Benutzer in partdb-editor    → ["partdb-editor"]
Benutzer in partdb-readonly  → ["partdb-readonly"]
```

Ein Benutzer kann mehrere Werte erhalten. Welche lokale Part-DB-Gruppe am Ende verwendet wird, bestimmt später die Reihenfolge in `PARTDB_SAML_ROLE_MAPPING`.

## 8. Native SAML-Anwendung `Part-DB SSO` anlegen

Navigation:

```text
Applications → Applications
```

Neue Anwendung mit SAML Provider erstellen.

### Anwendung

```text
Name: Part-DB SSO
Slug: partdb-sso
Group: Part-DB
Policy Engine Mode: ANY
Launch URL: https://partdb.<DOMAIN>/
```

Der Slug `partdb-sso` ist fest, weil der vorhandene Part-DB-Entrypoint daraus folgende IdP-URLs ableitet:

```text
https://auth.<DOMAIN>/application/saml/partdb-sso/metadata/
https://auth.<DOMAIN>/application/saml/partdb-sso/
```

## 9. SAML Provider konfigurieren

Getestete Konfiguration für Authentik 2026.5:

```text
Name: Provider for Part-DB SSO
Authorization Flow: default-provider-authorization-implicit-consent
Authentication Flow: default-authentication-flow
Invalidation Flow: default-provider-invalidation-flow

ACS URL: https://partdb.<DOMAIN>/saml/acs
Audience: https://partdb.<DOMAIN>/sp
SLS URL: https://partdb.<DOMAIN>/logout
SLS Binding: POST
Logout method: Front-channel (Native)
```

### Zertifikate und Signaturen

```text
Signing Certificate: authentik Self-signed Certificate
Verification Certificate: Part-DB SAML SP
Encryption Certificate: leer

Sign assertions: aktiviert
Sign responses: aktiviert
Sign logout requests: deaktiviert
Sign logout responses: deaktiviert
```

`Verification Certificate` enthält ausschließlich das zuvor importierte öffentliche SP-Zertifikat. Authentik kann damit Signaturen prüfen, die von Part-DB mit dem lokalen SP-Private-Key erzeugt werden.

Das standardmäßig von Authentik erzeugte `authentik Self-signed Certificate` kann für diese Konfiguration verwendet werden. Authentik weist darauf hin, dass dieses Standardzertifikat normalerweise nur ein Jahr gültig ist. Bei einem späteren Wechsel des Signing-Zertifikats muss auch `secrets/authentik_saml_idp_certificate` in Part-DB aktualisiert werden.

### Property Mappings

Bei den normalen SAML-Property-Mappings nur das für Part-DB benötigte Mapping auswählen:

```text
Part-DB Gruppen
```

NameID Property Mapping:

```text
authentik default SAML Mapping: Username
```

Part-DB ordnet SAML-Benutzer anhand des Benutzernamens dem lokalen Benutzer zu. Authentik-Benutzernamen sollten deshalb nach produktiver Nutzung nicht unnötig geändert werden.

### Weitere Protokollwerte

```text
AuthnContextClassRef Mapping: leer
Assertion valid not before: minutes=-5
Assertion valid not on or after: minutes=5
Session valid not on or after: minutes=86400
Default Relay State: leer
EntityID / Issuer Override: leer
Service Provider Binding: POST
Default NameID Policy: Persistent
Digest Algorithm: SHA256
Signature Algorithm: RSA-SHA256
```

Authentik 2026.5 verwendet für SAML einen vereinheitlichten SSO/SLO-Endpunkt. Deshalb sind für dieses Projekt SSO und SLO auf dieselbe Authentik-URL unter `/application/saml/partdb-sso/` gesetzt.

## 10. Bindings für `Part-DB SSO`

Dieselben Gruppen wie beim äußeren Access-Provider binden:

| Gruppe | Order | Enabled | Negate | Timeout | Failure result |
|---|---:|---|---|---:|---|
| `partdb-admin` | 0 | Ja | Nein | 30 | fail |
| `partdb-editor` | 10 | Ja | Nein | 30 | fail |
| `partdb-readonly` | 20 | Ja | Nein | 30 | fail |

Damit kann ein Benutzer nicht zwar die äußere Forward-Auth-Schicht passieren, aber den SAML-Provider ohne passende Part-DB-Gruppe frei benutzen.

## 11. Authentik-Metadaten prüfen

Metadata-URL:

```text
https://auth.<DOMAIN>/application/saml/partdb-sso/metadata/
```

Bei Produktionszertifikat:

```bash
curl -fsSL \
  https://auth.<DOMAIN>/application/saml/partdb-sso/metadata/ \
  -o /tmp/partdb-authentik-metadata.xml
```

Bei Staging:

```bash
curl -kfsSL \
  https://auth.<DOMAIN>/application/saml/partdb-sso/metadata/ \
  -o /tmp/partdb-authentik-metadata.xml
```

Grundwerte kontrollieren:

```bash
grep -Eo 'entityID="[^"]+"' \
  /tmp/partdb-authentik-metadata.xml \
  | head -n1

grep -Eo 'SingleSignOnService[^>]+Location="[^"]+"' \
  /tmp/partdb-authentik-metadata.xml \
  | head -n1
```

Für Authentik 2026.5 wird erwartet:

```text
EntityID:
https://auth.<DOMAIN>/application/saml/partdb-sso/metadata/

SSO/SLO-Endpunkt:
https://auth.<DOMAIN>/application/saml/partdb-sso/
```

## 12. Authentik-IdP-Zertifikat für Part-DB extrahieren

Der Part-DB-Entrypoint erwartet das X.509-Zertifikat aus den IdP-Metadaten als Base64-kodierte DER-Daten ohne PEM-Zeilen.

```bash
cd <PROJEKT_ROOT>/Compose/partdb

IDP_CERT="$({
  tr -d '\n\r\t ' < /tmp/partdb-authentik-metadata.xml
} | sed -n 's#.*<[^>]*X509Certificate[^>]*>\([^<]*\)</[^>]*X509Certificate>.*#\1#p')"

if [ -z "$IDP_CERT" ]; then
  echo 'Kein X509Certificate in den Authentik-Metadaten gefunden.' >&2
  exit 1
fi

printf '%s' "$IDP_CERT" \
  > secrets/authentik_saml_idp_certificate

unset IDP_CERT
chmod 600 secrets/authentik_saml_idp_certificate
rm -f /tmp/partdb-authentik-metadata.xml
```

Zertifikat validieren:

```bash
base64 -d secrets/authentik_saml_idp_certificate \
  | openssl x509 -inform DER -noout \
      -subject \
      -issuer \
      -dates \
      -fingerprint -sha256
```

Der Befehl muss ein gültiges Zertifikat ausgeben. Ein Base64- oder ASN.1-Fehler bedeutet, dass die Extraktion nicht korrekt war.

Wenn Authentik während einer Zertifikatsrotation mehrere Signing-Zertifikate gleichzeitig in den Metadaten veröffentlicht, nicht blind einen beliebigen Block übernehmen. In diesem Fall das tatsächlich beim Provider aktive Signing-Zertifikat gezielt aus Authentik exportieren und entsprechend als Base64-DER speichern.

## 13. Alle Part-DB-Secrets prüfen

```bash
cd <PROJEKT_ROOT>/Compose/partdb

for secret in \
  partdb_app_secret \
  mariadb_password \
  mariadb_root_password \
  authentik_saml_idp_certificate \
  partdb_saml_sp_certificate \
  partdb_saml_sp_private_key
do
  test -s "secrets/$secret" \
    || { echo "Fehlt oder leer: secrets/$secret" >&2; exit 1; }
done

stat -c '%A %s Bytes %n' secrets/*
```

Alle Dateien müssen vorhanden, nicht leer und mit Modus `600` geschützt sein.

## 14. Weiter

Jetzt ist die Authentik-Seite der Installation vollständig genug für den ersten Part-DB-Start:

- [Erststart und Prüfung](erststart-und-pruefung.md)

## Offizielle Referenzen

- [Authentik: Forward Auth](https://docs.goauthentik.io/add-secure-apps/providers/proxy/forward_auth/)
- [Authentik: Proxy Provider erstellen](https://docs.goauthentik.io/add-secure-apps/providers/proxy/create-proxy-provider/)
- [Authentik: SAML Provider erstellen](https://docs.goauthentik.io/add-secure-apps/providers/saml/create-saml-provider/)
- [Authentik: SAML Provider](https://docs.goauthentik.io/add-secure-apps/providers/saml/)
- [Authentik: Provider Property Mappings](https://docs.goauthentik.io/add-secure-apps/providers/property-mappings/)
- [Authentik: Zertifikate](https://docs.goauthentik.io/sys-mgmt/certificates/)
- [Authentik 2026.5 Release Notes](https://docs.goauthentik.io/releases/2026.5/)
- [Part-DB: SAML SSO](https://docs.part-db.de/installation/saml_sso.html)
