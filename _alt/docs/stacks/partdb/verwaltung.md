# Part-DB-Stack: Verwaltung und Anwendungseinstellungen

Dieses Dokument beschreibt die anwendungsspezifische Verwaltung nach erfolgreichem Erststart. Containerbetrieb, Logs und Neustarts stehen in [betrieb.md](betrieb.md).

## 1. Zwei Authentifizierungsebenen auseinanderhalten

Der normale Benutzerzugriff besteht aus zwei getrennten Prüfungen:

```text
Authentik Forward Auth
        ↓
Part-DB SAML-Login
```

Forward Auth entscheidet, ob der Browser die Anwendung überhaupt erreichen darf. SAML entscheidet anschließend, welcher Part-DB-Benutzer angemeldet wird und welche lokale Part-DB-Gruppe er erhält.

Eine erfolgreiche Authentik-Anmeldung bedeutet daher nicht automatisch, dass bereits eine Part-DB-Sitzung besteht.

## 2. Lokalen Notfalladministrator behalten

Der ursprüngliche Part-DB-Benutzer:

```text
admin
```

bleibt lokal.

Er wird nicht in einen SAML-Benutzer umgewandelt und erhält ein starkes, einzigartiges Passwort im Passwortmanager.

Zweck:

- SAML-Probleme beheben,
- fehlerhafte Gruppenmappings korrigieren,
- SAML-Zertifikate und Benutzerzustände diagnostizieren,
- einen von SAML unabhängigen Part-DB-Administrator behalten.

Der lokale `admin` **umgeht die äußere Authentik-Forward-Auth-Schicht nicht**. Bei einem vollständigen Authentik-Ausfall ist Part-DB über den normalen öffentlichen Zugriffspfad daher ebenfalls nicht erreichbar. Zuerst muss Authentik wiederhergestellt werden; ein separater Recovery-Pfad wäre eine eigene, bewusst zu entwerfende Sicherheitsarchitektur und ist nicht Teil dieses Projekts.

Passwort zurücksetzen:

```bash
cd <PROJEKT_ROOT>/Compose/partdb

docker compose exec partdb \
  /partdb-secret-entrypoint.sh \
  console partdb:users:set-password admin
```

Part-DB empfiehlt ausdrücklich, den ursprünglichen Administrator als lokalen Benutzer zu behalten.

## 3. SAML-Benutzer

Part-DB unterscheidet lokale Benutzer und SAML-Benutzer.

Ein SAML-Benutzer wird normalerweise beim ersten erfolgreichen SAML-Login automatisch erzeugt. Er besitzt kein lokales Part-DB-Passwort.

Wichtig: Part-DB ordnet SAML-Anmeldungen anhand des Benutzernamens zu. Authentik-Benutzernamen deshalb nach produktiver Nutzung nicht unüberlegt ändern; ein geänderter Name kann aus Sicht von Part-DB einen neuen Benutzer darstellen.

Vorhandene lokale Benutzer nicht ohne Migrationsgrund in SAML-Benutzer umwandeln. Falls dies später bewusst notwendig ist, Part-DB stellt dafür einen Konsolenbefehl bereit; der lokale Notfalladministrator ist davon ausgenommen.

## 4. Authentik-Gruppen und Part-DB-Gruppen

Authentik-Gruppen:

```text
partdb-admin
partdb-editor
partdb-readonly
```

Die Authentik-Gruppen steuern:

- die Bindings von `Part-DB Access`,
- die Bindings von `Part-DB SSO`,
- das SAML-Attribut `group`.

Part-DB übersetzt diese Werte über:

```text
PARTDB_SAML_ROLE_MAPPING
```

auf lokale numerische Gruppen-IDs.

Die IDs sind installationsabhängig und bleiben deshalb ausschließlich in `Compose/partdb/.env`.

## 5. Reihenfolge des Gruppenmappings

Empfohlenes Schema:

```dotenv
PARTDB_SAML_ROLE_MAPPING={"partdb-admin":<ADMIN_ID>,"partdb-editor":<EDITOR_ID>,"partdb-readonly":<READONLY_ID>,"*":-1}
```

Part-DB verwendet den **ersten passenden** Mapping-Eintrag. Deshalb steht die privilegierteste Rolle zuerst.

Nach einer Änderung:

```bash
cd <PROJEKT_ROOT>/Compose/partdb

docker compose config --quiet
docker compose up -d --force-recreate partdb
```

`SAML_UPDATE_GROUP_ON_LOGIN=true` ist im Wrapper aktiviert. Bei der nächsten SAML-Anmeldung wird die lokale Gruppe des Benutzers anhand der aktuellen SAML-Rollen erneut gesetzt.

## 6. Berechtigungen nicht nur über Gruppennamen beurteilen

Die Authentik-Gruppe steuert nur, auf **welche lokale Part-DB-Gruppe** gemappt wird. Die tatsächlichen Rechte kommen aus der Berechtigungskonfiguration dieser Part-DB-Gruppe.

Nach Änderungen an lokalen Gruppen deshalb kontrollieren:

- Part-DB-Administrator kann administrative Aufgaben ausführen,
- Editor kann die gewünschten Daten bearbeiten, aber nicht unnötig administrieren,
- Read-only kann lesen, aber keine Daten verändern,
- Benutzerrechte stehen möglichst auf `inherit`, wenn die Gruppe maßgeblich sein soll.

## 7. Anonymer Benutzer

Part-DB verwendet den speziellen Benutzer `anonymous` für nicht innerhalb der Anwendung angemeldete Requests.

Für die Projektkonfiguration:

- alle Anonymous-Berechtigungen auf **verboten**,
- Anonymous deaktivieren, soweit die Version dafür eine Aktiv-/Login-Einstellung anbietet.

Damit bleiben die beiden Schutzschichten konsistent:

```text
ohne Authentik-Sitzung → kein Zugriff auf Part-DB
mit Authentik-Sitzung, aber ohne Part-DB-Sitzung → keine Bestandsdaten
mit gültigem SAML-Login → Rechte der gemappten Part-DB-Gruppe
```

Nach Part-DB-Updates diese Negativtests erneut durchführen, da das Berechtigungssystem Teil der Anwendung ist.

## 8. Allgemeine Systemeinstellungen

Part-DB-Systemeinstellungen befinden sich abhängig von Sprache und Version unter dem Bereich:

```text
Tools → System → Settings
```

Dort können viele anwendungsspezifische Einstellungen verwaltet werden.

Einige Werte werden in diesem Projekt jedoch absichtlich als Umgebungsvariablen aus `.env` gesetzt, darunter:

```text
DEFAULT_LANG
DEFAULT_TIMEZONE
BASE_CURRENCY
INSTANCE_NAME
```

Der Wrapper erzeugt diese Werte aus den `PARTDB_*`-Variablen. Part-DB kann durch Umgebungsvariablen Web-UI-Einstellungen überschreiben; ein entsprechendes Feld kann daher gesperrt oder nach einem Neustart wieder durch den Env-Wert ersetzt werden.

Solche Basiseinstellungen werden in diesem Projekt über `.env` geändert, **nicht** durch manuelles Bearbeiten von `compose.yml`.

## 9. Basiswährung

`PARTDB_BASE_CURRENCY` legt die interne Basiswährung fest.

Diese Einstellung vor produktiver Erfassung von Preis- und Währungsdaten bewusst festlegen. Part-DB weist darauf hin, dass die Basiswährung nach vorhandenen Daten nicht beliebig geändert werden kann.

Eine Anzeige- beziehungsweise Benutzerwährung ist davon zu unterscheiden; Benutzer können je nach Part-DB-Konfiguration eigene Anzeigepräferenzen besitzen.

## 10. Informationsanbieter

Part-DB kann Informationen von externen Anbietern wie Distributoren und Herstellern beziehen.

Die Netzwerkarchitektur blockiert diesen Egress nicht: `partdb-server` hängt am nicht-internen Netzwerk `web` und kann reguläre ausgehende Verbindungen aufbauen.

Part-DB zeigt konfigurierte Informationsanbieter unter einem Pfad wie:

```text
Tools → Information Providers
```

beziehungsweise versionsabhängig unter:

```text
/tools/info_providers/providers
```

Für die Nutzung sind passende Part-DB-Berechtigungen erforderlich.

### Zugangsdaten

Je nach Anbieter verwendet Part-DB:

- API-Schlüssel,
- API-Secret,
- OAuth-Verbindung,
- zusätzliche Länder-, Sprach- oder Währungseinstellungen.

Anbietersecrets niemals in Git dokumentieren.

Wo Part-DB eine sichere Konfiguration über die Weboberfläche beziehungsweise einen OAuth-Flow anbietet, diese Möglichkeit verwenden.

Viele Provider-Optionen sind laut Part-DB-Dokumentation jedoch `PROVIDER_*`-Umgebungsvariablen. Die lokale Docker-Compose-`.env` injiziert zusätzliche Variablen **nicht automatisch** in den Container. Wenn für einen Provider eine ausschließlich env-basierte Option benötigt wird, wird dafür eine bewusste, versionierte Erweiterung des Stackdesigns vorgenommen. Die installierte `compose.yml` wird nicht ad hoc pro Server bearbeitet.

## 11. Ausgehende Verbindung testen

Grundlegendes DNS aus dem Part-DB-Container:

```bash
cd <PROJEKT_ROOT>/Compose/partdb

docker compose exec partdb \
  getent ahostsv4 github.com
```

Der konkrete Provider-Test sollte anschließend aus der Part-DB-Oberfläche erfolgen, damit auch API-Zugangsdaten, Berechtigungen und Providerlogik geprüft werden.

## 12. Part-DB-Konsolenbefehle

Der Wrapper besitzt einen speziellen `console`-Modus. Dadurch werden vor dem Aufruf alle normalen Secrets und Env-Werte geladen und der Symfony-Befehl als `www-data` ausgeführt.

Allgemeines Muster:

```bash
docker compose exec partdb \
  /partdb-secret-entrypoint.sh \
  console <PARTDB-KONSOLENBEFEHL>
```

Beispiele:

```bash
# Benutzer auflisten
docker compose exec partdb \
  /partdb-secret-entrypoint.sh \
  console partdb:users:list

# Passwort eines lokalen Benutzers ändern
docker compose exec partdb \
  /partdb-secret-entrypoint.sh \
  console partdb:users:set-password admin

# Cache leeren
docker compose exec partdb \
  /partdb-secret-entrypoint.sh \
  console cache:clear
```

Keine Konsolenbefehle als Root mit abweichender Umgebung ausführen, wenn dadurch eine andere Part-DB-Konfiguration verwendet würde.

## 13. SAML-SP-Zertifikat überwachen

Das lokale SP-Schlüsselpaar wurde bei der Installation mit einer begrenzten Laufzeit erzeugt.

Ablaufdatum prüfen:

```bash
cd <PROJEKT_ROOT>/Compose/partdb

base64 -d secrets/partdb_saml_sp_certificate \
  | openssl x509 -inform DER -noout -subject -dates
```

Vor Ablauf wird ein neues SP-Schlüsselpaar geplant erzeugt, das neue **öffentliche** Zertifikat in Authentik als Verification Certificate eingetragen und anschließend die lokalen Part-DB-Secrets gemeinsam umgestellt.

Nicht nur eine Seite des Schlüsselpaars austauschen.

## 14. Authentik-IdP-Zertifikat überwachen

Part-DB vertraut dem Inhalt von:

```text
secrets/authentik_saml_idp_certificate
```

Wenn das Signing Certificate des Authentik-SAML-Providers gewechselt wird, muss dieses lokale Secret zum neuen aktiven IdP-Zertifikat passen. Wird weiterhin das standardmäßig erzeugte `authentik Self-signed Certificate` verwendet, ist dessen Laufzeit laut Authentik standardmäßig ein Jahr; der Ablauf muss deshalb in die regelmäßige Wartung aufgenommen werden.

Aktuellen lokalen Inhalt prüfen:

```bash
base64 -d secrets/authentik_saml_idp_certificate \
  | openssl x509 -inform DER -noout \
      -subject \
      -issuer \
      -dates \
      -fingerprint -sha256
```

Danach Part-DB neu erstellen:

```bash
docker compose up -d --force-recreate partdb
```

## 15. API, KiCad und MCP

Maschinenzugriffe werden bewusst getrennt dokumentiert:

- [API, KiCad und MCP](api-kicad-und-mcp.md)

Die Basiskonfiguration enthält **keine** unauthentifizierte Traefik-Ausnahme für diese Endpunkte.

## Offizielle Referenzen

- [Part-DB: Getting started](https://docs.part-db.de/usage/getting_started.html)
- [Part-DB: SAML SSO](https://docs.part-db.de/installation/saml_sso.html)
- [Part-DB: Konfiguration](https://docs.part-db.de/configuration.html)
- [Part-DB: Information provider system](https://docs.part-db.de/usage/information_provider_system.html)
- [Part-DB: Console commands](https://docs.part-db.de/usage/console_commands.html)
