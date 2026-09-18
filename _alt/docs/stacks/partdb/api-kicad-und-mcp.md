# Part-DB-Stack: REST-API, KiCad und MCP

Dieses Dokument beschreibt den **aktuellen Sicherheitsstand** und die Voraussetzungen für Maschinenzugriffe.

## 1. Aktueller Projektzustand

Der Part-DB-Traefik-Router verwendet für alle normalen Pfade:

```text
authentik@docker
```

Es gibt derzeit **keine** Ausnahme für:

```text
/api
/<sprache>/kicad-api/
/mcp
```

Damit bleiben auch diese Pfade hinter der äußeren Authentik-Forward-Auth-Schicht.

Das ist absichtlich die sichere Basiskonfiguration.

## 2. Warum Browser-SSO und API-Token unterschiedliche Dinge sind

Part-DB authentifiziert API-Clients mit einem eigenen API-Token im HTTP-Header:

```text
Authorization: Bearer <PARTDB_API_TOKEN>
```

Traefik führt jedoch **vorher** die Authentik-Forward-Auth-Prüfung aus.

Ein Maschinenclient, der nur einen gültigen Part-DB-API-Token kennt, besitzt normalerweise keine interaktive Authentik-Browsersitzung. Deshalb kann er in der aktuellen Basiskonfiguration bereits an Forward Auth scheitern, bevor Part-DB den Bearer-Token auswertet.

Das ist kein Part-DB-Tokenfehler, sondern Folge der bewusst vorgeschalteten Schutzschicht.

## 3. REST-API von Part-DB

Part-DB stellt die REST-API unter:

```text
https://partdb.<DOMAIN>/api/
```

bereit.

Part-DB selbst verlangt dafür:

- passende Benutzerberechtigungen für die API,
- Berechtigung zum Erzeugen von API-Tokens,
- einen API-Token mit möglichst kleinem Scope.

Part-DB dokumentiert die API weiterhin als Beta und empfiehlt die Nutzung nur mit vertrauenswürdigen Benutzern und Anwendungen.

API-Tokens sind Secrets und werden nicht in Git, Markdown-Dateien oder Shell-History gespeichert.

## 4. KiCad-Integration

Part-DB unterstützt die HTTP-Library-Funktion von KiCad 8 oder neuer.

Der Part-DB-Endpunkt lautet sprachabhängig beispielsweise:

```text
https://partdb.<DOMAIN>/de/kicad-api/
```

oder:

```text
https://partdb.<DOMAIN>/en/kicad-api/
```

Die tatsächlich für den Benutzer vorgesehene URL kann in Part-DB bei den API-Endpunkten angezeigt werden.

KiCad benötigt außerdem einen Part-DB-API-Token.

Für regulären externen Einsatz sollte Part-DB ein öffentlich vertrauenswürdiges TLS-Zertifikat besitzen. Staging- oder selbstsignierte Zertifikate sind für Maschinenclients ungeeignet beziehungsweise werden von KiCad nicht ohne Weiteres akzeptiert.

## 5. MCP

Part-DB besitzt einen MCP-Server unter:

```text
https://partdb.<DOMAIN>/mcp
```

Besonderheiten laut Part-DB-Dokumentation:

- MCP ist standardmäßig deaktiviert,
- Aktivierung erfolgt durch einen Administrator in den Systemeinstellungen im AI-Bereich oder über die entsprechende Konfiguration,
- Benutzer benötigen die Berechtigung `Use MCP tools`,
- Authentifizierung erfolgt ebenfalls per Part-DB-API-Token,
- der aktuelle MCP-Zugriff ist read-only,
- Transport ist Streamable HTTP.

Das Aktivieren des MCP-Schalters in Part-DB ändert **nicht** die äußere Traefik-Forward-Auth-Schicht.

## 6. Warum jetzt keine pauschale Ausnahme eingerichtet wird

Eine allgemeine Ausnahme wie:

```text
/api/* ohne Authentik
```

würde die Sicherheitsgrenze des Projekts verändern.

Das ist insbesondere deshalb relevant, weil:

- Part-DBs REST-API laut eigener Dokumentation noch Beta ist,
- ein gestohlener API-Token die Rechte des zugehörigen Benutzers ausübt,
- verschiedene Maschinenendpunkte unterschiedliche Berechtigungen und Risiken besitzen,
- eine zu breite Traefik-Regel unbeabsichtigt weitere Part-DB-Seiten umgehen könnte.

Deshalb gibt es im normalen Installationsablauf **keine** manuelle Änderung an `compose.yml`.

## 7. Falls Maschinenzugriff später benötigt wird

Eine spätere Freigabe wird als eigene, versionierte Architekturänderung geplant. Sie ist **keine** installationsspezifische Handänderung auf einem einzelnen Server.

Vor einer solchen Änderung müssen mindestens festgelegt werden:

1. welcher exakte Pfad benötigt wird,
2. welcher Client ihn benutzt,
3. welche Part-DB-Berechtigungen der zugehörige Benutzer besitzt,
4. welcher API-Token-Scope erforderlich ist,
5. ob der Endpunkt ohne Authentik wirklich erreichbar sein muss,
6. wie Requests ohne oder mit ungültigem Part-DB-Token abgewiesen werden,
7. ob die Regel weitere Pfade unbeabsichtigt freigibt.

Nach einer Implementierung sind mindestens folgende Negativtests erforderlich:

```text
kein Part-DB-Token                  → abgewiesen
ungültiger Part-DB-Token            → abgewiesen
gültiger Token ohne Berechtigung    → abgewiesen
gültiger minimaler Token            → nur vorgesehene Aktion erlaubt
andere Part-DB-Webpfade              → weiterhin Authentik-geschützt
```

## 8. Token-Prinzipien

Für alle Part-DB-API-Tokens:

- pro Anwendung ein eigener Token,
- kleinstmöglicher Scope,
- dedizierter Part-DB-Benutzer, wenn fachlich sinnvoll,
- Benutzerrechte ebenfalls minimal halten,
- Ablaufdatum verwenden, wenn praktikabel,
- Token bei Verlust sofort löschen beziehungsweise ersetzen,
- niemals gemeinsam mit Konfigurationsdateien in Git speichern.

## 9. Kein Konflikt mit normalem Browserbetrieb

Die aktuelle Basiskonfiguration ist für Browsernutzer vollständig:

```text
Browser → Authentik Forward Auth → Part-DB → SAML
```

Die fehlende Maschinenfreigabe ist deshalb **kein unvollständiger Webaufbau**, sondern eine bewusst noch nicht aktivierte zusätzliche Zugriffsmöglichkeit.

## Offizielle Referenzen

- [Part-DB: REST API Introduction](https://docs.part-db.de/api/intro.html)
- [Part-DB: API Authentication](https://docs.part-db.de/api/authentication.html)
- [Part-DB: EDA / KiCad integration](https://docs.part-db.de/usage/eda_integration.html)
- [Part-DB: MCP Server](https://docs.part-db.de/api/mcp.html)
- [Authentik: Forward Auth](https://docs.goauthentik.io/add-secure-apps/providers/proxy/forward_auth/)
