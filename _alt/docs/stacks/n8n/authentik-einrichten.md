# Authentik für n8n einrichten

n8n Community hat kein natives OIDC. Der Browserzugriff wird deshalb mit
Authentik Forward Auth geschützt; die n8n-Anmeldung bleibt lokal.

```text
Gruppen: n8n-users, n8n-admins
Initiales Mitglied: akadmin in beiden Gruppen
```

## Sichtbare Portal-Anwendung

```text
Anwendung: n8n
Slug: n8n
Kategorie: KI
Launch URL: https://n8n.<DOMAIN>/

Provider: n8n Access Provider
Typ: Proxy Provider
Mode: Forward auth (single application)
External host: https://n8n.<DOMAIN>/
```

Die Anwendung erhält eine Gruppenbindung zu `n8n-users` und wird dem
`authentik Embedded Outpost` zugeordnet. Die zwei Callback-URIs sind:

```text
https://n8n.<DOMAIN>/outpost.goauthentik.io/callback?X-authentik-auth-callback=true
https://n8n.<DOMAIN>/?X-authentik-auth-callback=true
```

Der Traefik-Outpost-Pfad erhält keine `authentik`-Middleware. Nach Änderungen
an Provider oder Callback-URIs Cookies für `auth.<DOMAIN>` und
`n8n.<DOMAIN>` löschen oder ein privates Browserfenster verwenden.

Weiter mit [Erststart und Prüfung](erststart-und-pruefung.md).
