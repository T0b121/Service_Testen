# Authentik für Qdrant einrichten

Qdrant bietet kein natives OIDC für seine Web UI. Authentik Forward Auth
schützt deshalb den Browserzugriff; Qdrants eigener API-Schlüssel schützt
zusätzlich alle REST- und gRPC-Aufrufe.

Die produktive Konfiguration wurde direkt in Authentik angelegt:

```text
Gruppe: qdrant-users
Mitglied: akadmin

Anwendung: Qdrant Access
Slug: qdrant-access
Portal-Kategorie: Betrieb
Launch URL: https://qdrant.<DOMAIN>/dashboard/

Provider: Qdrant Access Provider
Typ: Proxy Provider
Mode: Forward auth (single application)
External host: https://qdrant.<DOMAIN>/
Authorization flow: default-provider-authorization-implicit-consent
```

Die Anwendung besitzt eine aktive, nicht negierte Gruppenbindung zu
`qdrant-users` mit Reihenfolge `0`, Timeout `30` und Fehlerergebnis `fail`.
Der Provider ist dem `authentik Embedded Outpost` zugeordnet.

Die beiden strikt abgeglichenen Redirect-URIs lauten:

```text
https://qdrant.<DOMAIN>/outpost.goauthentik.io/callback?X-authentik-auth-callback=true
https://qdrant.<DOMAIN>/?X-authentik-auth-callback=true
```

Weitere Personen erhalten Dashboardzugriff ausschließlich durch Mitgliedschaft
in `qdrant-users`. Der API-Schlüssel wird dadurch nicht ersetzt und darf nicht
in Authentik, Traefik-Labels oder Browser-URLs gespeichert werden.

Weiter mit [Erststart und Prüfung](erststart-und-pruefung.md).
