# Authentik für Langfuse einrichten

Langfuse verwendet zwei Schichten: Forward Auth begrenzt den Browserzugriff
vor der Anwendung. Die Anwendung führt danach die eigentliche, native
Authentik-OIDC-Anmeldung aus. Beide sind auf `langfuse-users` gebunden.

```text
Gruppen: langfuse-users, langfuse-admins
Initiales Mitglied: akadmin in beiden Gruppen
```

## Sichtbare Portal-Anwendung

```text
Anwendung: Langfuse Access
Slug: langfuse-access
Kategorie: KI
Launch URL: https://langfuse.<DOMAIN>/api/auth/signin/authentik
Icon: https://langfuse.com/favicon.ico

Provider: Langfuse Access Provider
Typ: Proxy Provider
Mode: Forward auth (single application)
External host: https://langfuse.<DOMAIN>/
```

Die Anwendung besitzt eine aktive Gruppenbindung zu `langfuse-users` und ist
dem `authentik Embedded Outpost` zugeordnet.

## Ausgeblendete technische OIDC-Anwendung

```text
Anwendung: Langfuse
Slug: langfuse
Kategorie: KI
Metadatum meta_hide: true

Provider: Langfuse OIDC Provider
Typ: OAuth2/OpenID Provider
Client type: confidential
Client ID: langfuse
Signing key: authentik Self-signed Certificate
```

Die streng abgeglichene OAuth2-Redirect-URI lautet:

```text
https://langfuse.<DOMAIN>/api/auth/callback/authentik
```

Scopes: `openid`, `profile`, `email`. Der E-Mail-Scope ist zwingend, weil
Langfuse die bestehende Initialidentität sicher über die E-Mail verknüpft.
`meta_hide: true` unterdrückt nur die technische Kachel für normale Nutzer;
Authentik-Administratoren können sie weiterhin verwalten.

Die produktive Konfiguration wurde idempotent über die Authentik-Shell
eingerichtet. Die spätere zentrale Einrichtungs-CLI muss beide Provider,
Gruppen, Bindings, Outpost-Zuordnung, OIDC-Client-Secret und die versteckte
Kachel gleichermaßen reproduzieren.

Weiter mit [Erststart und Prüfung](erststart-und-pruefung.md).
