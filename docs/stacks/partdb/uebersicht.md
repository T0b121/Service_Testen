# Part-DB-Stack: Übersicht

## 1. Zweck

Der Stack stellt eine zentral erreichbare Part-DB-Installation mit eigener MariaDB-Datenbank bereit.

Die Sicherheitsarchitektur besteht aus zwei getrennten Ebenen:

1. **Äußere Zugriffskontrolle:** Traefik sendet jeden normalen Request zuerst an Authentik Forward Auth.
2. **Anwendungsanmeldung:** Nach erfolgreicher äußerer Authentifizierung meldet sich der Benutzer innerhalb von Part-DB über natives SAML-SSO an.

Dadurch ist Part-DB nicht bereits vor einer Authentik-Anmeldung öffentlich lesbar. Die SAML-Anmeldung übernimmt anschließend Benutzeridentität und Part-DB-Gruppenzuordnung.

Part-DB kennzeichnet seine SAML-Unterstützung derzeit als **Beta**. Die in diesem Projekt dokumentierte Kombination mit Authentik wurde praktisch getestet, muss aber insbesondere nach Part-DB- oder Authentik-Updates erneut mit einem vollständigen SAML-Login und der Gruppenzuordnung geprüft werden.

## 2. Vorausgesetzte Stacks

Erforderlich:

- `core`

Der Core-Stack stellt bereit:

- Traefik,
- TLS/ACME,
- das externe Docker-Netzwerk `web`,
- Authentik,
- die Forward-Auth-Middleware `authentik@docker`,
- den Outpost-Router für `partdb.<DOMAIN>/outpost.goauthentik.io/`.

Part-DB darf erst öffentlich getestet werden, wenn der Core-Stack gesund ist und Authentik funktioniert.

## 3. Dienste

| Compose-Dienst | Container | Aufgabe | Öffentlich |
|---|---|---|---|
| `partdb` | `partdb-server` | Part-DB-Webanwendung, SAML-SP, REST-API, KiCad-API, optional MCP | nur über Traefik |
| `mariadb` | `partdb-mariadb` | Part-DB-Datenbank | Nein |

## 4. Öffentlicher Endpunkt

```text
https://partdb.<DOMAIN>
```

Es gibt kein direktes Host-Portmapping auf Part-DB. Der im Container sichtbare Port `80/tcp` ist ausschließlich ein Containerport.

## 5. Zugriffspfad

Normaler Webrequest:

```text
Browser
  ↓ HTTPS :443
Traefik
  ↓ ForwardAuth
Authentik Embedded Outpost
  ↓ erlaubt
Traefik
  ↓ HTTP innerhalb Docker-Netzwerk web
Part-DB :80
```

SAML-Anmeldung innerhalb von Part-DB:

```text
Part-DB Login
  ↓
Authentik SAML Provider
  ↓ SAML Response
https://partdb.<DOMAIN>/saml/acs
  ↓
Part-DB-Benutzer und Gruppenzuordnung
```

Die beiden Mechanismen erfüllen unterschiedliche Aufgaben und ersetzen einander nicht.

## 6. Traefik-Router

### Part-DB-Anwendung

Der Router wird im Part-DB-Stack definiert:

```text
Host partdb.<DOMAIN>
EntryPoint websecure
TLS Resolver letsencrypt
Middleware authentik@docker
Service partdb:80
```

### Authentik-Outpost

Der erforderliche Outpost-Router wird ebenfalls im Part-DB-Stack definiert:

```text
Host partdb.<DOMAIN>
Pfad /outpost.goauthentik.io/
Ziel Authentik Server
Priorität 100
keine Forward-Auth-Middleware
```

Der Router verwendet den vom Core-Stack bereitgestellten Traefik-Service `authentik@docker`. Der Outpost-Pfad darf nicht erneut durch dieselbe Forward-Auth-Middleware geschützt werden, sonst kann die Authentifizierung nicht abgeschlossen werden.

## 7. Netzwerke

### `web`

Externes gemeinsames Proxy-Netzwerk.

Enthält für diesen Stack:

```text
partdb-server
```

Außerdem befinden sich dort unter anderem Traefik und Authentik Server aus dem Core-Stack.

Zweck:

- Traefik erreicht Part-DB.
- Part-DB erreicht Dienste im `web`-Netzwerk, soweit diese dort erreichbar sind.
- Part-DB besitzt regulären ausgehenden Netzwerkzugriff und kann beispielsweise externe Informationsanbieter abfragen.

### `partdb_internal`

Internes Stack-Netzwerk:

```text
partdb-server
partdb-mariadb
```

Eigenschaft:

```yaml
internal: true
```

MariaDB hängt ausschließlich in diesem Netzwerk und besitzt keinen Host-Port.

## 8. Persistente Volumes

| Volume | Inhalt |
|---|---|
| `partdb_uploads` | hochgeladene Anhänge und Part-DB-interne Automigrationsbackups |
| `partdb_public_media` | generierte beziehungsweise hochgeladene öffentliche Mediendateien |
| `partdb_mariadb_data` | MariaDB-Datenverzeichnis |

Datenbank und Dateivolumes gehören gemeinsam in ein konsistentes Backup.

## 9. Lokale Konfigurationsdateien

Versioniert:

```text
Compose/partdb/compose.yml
Compose/partdb/config/zz-partdb.ini
Compose/partdb/scripts/partdb-entrypoint.sh
```

Nicht versioniert:

```text
Compose/partdb/.env
Compose/partdb/secrets/
```

Die versionierten Docker-Dateien werden bei einer normalen Installation nicht verändert.

## 10. `.env`-Werte

Der Stack erwartet:

```text
DOMAIN
PARTDB_VERSION
MARIADB_VERSION
PARTDB_DEFAULT_LANG
PARTDB_DEFAULT_TIMEZONE
PARTDB_BASE_CURRENCY
PARTDB_INSTANCE_NAME
PARTDB_SAML_ROLE_MAPPING
MARIADB_DATABASE
MARIADB_USER
```

Die konkrete Part-DB-URL, Trusted Hosts, Datenbank-URL und SAML-Endpunkte werden im Wrapper daraus abgeleitet.

## 11. Secrets

| Secret-Datei | Zweck |
|---|---|
| `secrets/partdb_app_secret` | Symfony/Part-DB-Anwendungssecret |
| `secrets/mariadb_password` | Passwort des Part-DB-Datenbankbenutzers |
| `secrets/mariadb_root_password` | MariaDB-Rootpasswort |
| `secrets/authentik_saml_idp_certificate` | öffentlicher IdP-Signaturzertifikatsinhalt für Part-DB |
| `secrets/partdb_saml_sp_certificate` | öffentliches Zertifikat des Part-DB-SAML-Service-Providers |
| `secrets/partdb_saml_sp_private_key` | privater SAML-SP-Schlüssel von Part-DB |

Alle Dateien bleiben installationsspezifisch und werden nicht in Git gespeichert.

## 12. SAML-Konventionen

Der Wrapper leitet aus `DOMAIN` folgende Werte ab:

```text
DEFAULT_URI=https://partdb.<DOMAIN>/
SAML_IDP_ENTITY_ID=https://auth.<DOMAIN>/application/saml/partdb-sso/metadata/
SAML_IDP_SINGLE_SIGN_ON_SERVICE=https://auth.<DOMAIN>/application/saml/partdb-sso/
SAML_IDP_SINGLE_LOGOUT_SERVICE=https://auth.<DOMAIN>/application/saml/partdb-sso/
SAML_SP_ENTITY_ID=https://partdb.<DOMAIN>/sp
```

Damit sind folgende Werte Projektkonventionen:

- Part-DB-Subdomain: `partdb`
- Authentik-SAML-Application-Slug: `partdb-sso`

Die **Basisdomain** bleibt vollständig über `DOMAIN` austauschbar.

## 13. Gruppenmodell

Authentik verwendet:

```text
partdb-admin
partdb-editor
partdb-readonly
```

Diese Gruppen steuern sowohl den äußeren Zugang zu Part-DB als auch die SAML-Gruppeninformation.

In Part-DB werden diese Namen über `PARTDB_SAML_ROLE_MAPPING` auf die **lokalen numerischen Gruppen-IDs der jeweiligen Installation** abgebildet.

Die IDs dürfen nicht als allgemein gültige Werte behandelt oder in versionierte Dateien eingebaut werden. Sie werden nach dem ersten Start aus der lokalen Part-DB-Installation gelesen und anschließend nur in `.env` gespeichert.

## 14. Lokaler Notfalladministrator

Der initiale Part-DB-Benutzer `admin` bleibt ein lokaler Benutzer.

Er dient als anwendungsseitiger Notfallzugang, wenn beispielsweise SAML oder das Gruppenmapping fehlerhaft ist.

Wichtig: Der lokale Part-DB-Administrator **umgeht die äußere Forward-Auth-Schicht nicht**. Ist Authentik vollständig ausgefallen, ist der normale öffentliche Part-DB-Pfad ebenfalls blockiert. Für eine solche Störung muss der Administrator zuerst Authentik wiederherstellen oder einen bewusst eingerichteten lokalen Recovery-Zugriff verwenden; die Basiskonfiguration öffnet dafür keinen öffentlichen Bypass.

Dieser Benutzer sollte ein starkes, einzigartiges Passwort besitzen und nicht in einen SAML-Benutzer umgewandelt werden.

## 15. Anonymer Benutzer

Part-DB besitzt einen besonderen Benutzer `anonymous`. Dessen Rechte gelten für Benutzer, die innerhalb von Part-DB noch nicht angemeldet sind.

Für dieses Projekt wird der Benutzer nach dem Erststart so restriktiv wie möglich konfiguriert:

- Anmeldung beziehungsweise Aktivität deaktivieren, soweit die Oberfläche dies anbietet,
- alle Berechtigungen explizit auf **verboten** setzen.

Die äußere Authentik-Schicht bleibt trotzdem erforderlich. Part-DB-eigene Anonymous-Rechte sind kein Ersatz für Forward Auth.

## 16. Datenbankmigrationen

Der Stack setzt:

```text
DB_AUTOMIGRATE=true
```

Part-DB führt dadurch erforderliche Datenbankmigrationen beim Containerstart automatisch aus. Die Part-DB-Dokumentation kennzeichnet diese Funktion als experimentell.

Daher gilt insbesondere vor Updates:

- vollständiges Backup erstellen,
- Logs der Migration beobachten,
- das unter `uploads/.automigration-backup` erzeugte Automigrationsbackup nicht als einziges Backup betrachten.

## 17. PHP-Konfiguration für große Projekte

Die Datei:

```text
Compose/partdb/config/zz-partdb.ini
```

setzt:

```ini
max_input_vars = 10000
```

Sie wird sowohl für PHP-FPM als auch für PHP-CLI eingebunden. Dadurch können große Part-DB-Projektformulare mit vielen Komponenten verarbeitet werden, ohne dass die Standardgrenze von PHP zu früh greift.

## 18. API, KiCad und MCP

Im aktuellen Sicherheitsmodell schützt Forward Auth den gesamten Part-DB-Router. Es gibt keine allgemeine Ausnahme für:

```text
/api
/mcp
/<sprache>/kicad-api/
```

Browserzugriff und Maschinenzugriff sind deshalb getrennt zu betrachten. Details:

- [API, KiCad und MCP](api-kicad-und-mcp.md)

## 19. Zu sichernde Daten

Mindestens:

- `compose.yml`, `config/` und `scripts/` über Git,
- lokale `.env`,
- alle sechs Secret-Dateien,
- MariaDB-Dump,
- `partdb_uploads`,
- `partdb_public_media`,
- verwendete Image-Versionen,
- Authentik-Konfiguration für `Part-DB Access` und `Part-DB SSO`.

Details:

- [Part-DB: Backup und Wiederherstellung](backup-und-wiederherstellung.md)

## Offizielle Referenzen

- [Part-DB: Docker-Installation](https://docs.part-db.de/installation/installation_docker.html)
- [Part-DB: Konfiguration](https://docs.part-db.de/configuration.html)
- [Part-DB: Reverse Proxy](https://docs.part-db.de/installation/reverse-proxy.html)
- [Part-DB: SAML SSO](https://docs.part-db.de/installation/saml_sso.html)
- [Authentik: Forward Auth](https://docs.goauthentik.io/add-secure-apps/providers/proxy/forward_auth/)
- [Authentik: SAML Provider](https://docs.goauthentik.io/add-secure-apps/providers/saml/)
