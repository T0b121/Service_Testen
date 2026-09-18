# Authentik für Flowise einrichten

Flowise Community unterstützt kein natives OIDC. Der Browserzugriff wird daher
vor der Anwendung mit Authentik Forward Auth geschützt. Die anschließende
Flowise-Anmeldung bleibt absichtlich lokal und ist eine zweite Schutzschicht.

```text
Gruppen: flowise-users, flowise-admins
Initiales Mitglied: akadmin in beiden Gruppen
```

## Sichtbare Portal-Anwendung

```text
Anwendung: Flowise
Slug: flowise
Kategorie: KI
Launch URL: https://flowise.<DOMAIN>/
Icon: https://flowiseai.com/favicon.ico

Provider: Flowise Access Provider
Typ: Proxy Provider
Mode: Forward auth (single application)
External host: https://flowise.<DOMAIN>/
```

Die Anwendung besitzt eine aktive Gruppenbindung zu `flowise-users` und ist
dem `authentik Embedded Outpost` zugeordnet. Der Provider muss die OAuth2
Grant-Types `authorization_code`, `client_credentials` und `password`
enthalten. Fehlende Grant-Types führen trotz korrekter Callback-URL zu
`invalid_request`.

Die zwei strikt passenden Redirect-URIs lauten:

```text
https://flowise.<DOMAIN>/outpost.goauthentik.io/callback?X-authentik-auth-callback=true
https://flowise.<DOMAIN>/?X-authentik-auth-callback=true
```

Der Outpost-Pfad erhält in Traefik keine `authentik`-Middleware. Die spätere
Einrichtungs-CLI muss Gruppe, Gruppenbindung, Provider, beide Redirect-URIs,
Grant-Types, sichtbare Portal-Kachel und Outpost-Zuordnung reproduzieren.

Weiter mit [Erststart und Prüfung](erststart-und-pruefung.md).
