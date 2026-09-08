# Authentik für RustFS einrichten

RustFS verwendet absichtlich zwei Authentik-Schichten. Forward Auth schützt
den gesamten Browserweg bereits vor RustFS. Natives OIDC stellt anschließend
in der RustFS-Konsole die tatsächliche Konsolenidentität bereit. Beide
Schichten müssen dieselbe Gruppe `rustfs-admins` verlangen.

## Berechtigung

```text
Gruppe: rustfs-admins
Mitglied: akadmin
```

## Sichtbare Portal-Anwendung: Forward Auth

Diese Anwendung ist die einzige für normale Benutzer sichtbare Kachel.

```text
Anwendung: RustFS Console Access
Slug: rustfs-console-access
Kategorie: Betrieb
Launch URL: https://s3.<DOMAIN>/
Icon: https://rustfs.com/favicon.ico

Provider: RustFS Console Access Provider
Typ: Proxy Provider
Mode: Forward auth (single application)
External host: https://s3.<DOMAIN>/
Authorization flow: default-provider-authorization-implicit-consent
```

Die Anwendung besitzt eine aktive, nicht negierte Gruppenbindung zu
`rustfs-admins` (Reihenfolge `0`, Timeout `30`, Fehlerergebnis `fail`). Der
Provider ist dem `authentik Embedded Outpost` zugeordnet. Die strikt
abgeglichenen Callback-Adressen sind:

```text
https://s3.<DOMAIN>/outpost.goauthentik.io/callback?X-authentik-auth-callback=true
https://s3.<DOMAIN>/?X-authentik-auth-callback=true
```

## Versteckte technische OIDC-Anwendung

```text
Anwendung: RustFS Console
Slug: rustfs-console
Launch URL: leer
Metadatum meta_hide: true
Icon: https://rustfs.com/favicon.ico

Provider: RustFS Console OIDC Provider
Typ: OAuth2/OpenID Provider
Client type: confidential
Client ID: rustfs-console
Authorization flow: default-provider-authorization-implicit-consent
Signing key: authentik Self-signed Certificate
```

Die OAuth2-Redirect-URI muss exakt lauten:

```text
https://s3.<DOMAIN>/rustfs/admin/v3/oidc/callback/default
```

Scopes: `openid`, `profile`, `email`. Der Provider benötigt zwingend einen
Signing Key; ohne ihn liefert das JWKS keine verwendbaren Schlüssel und die
RustFS-Konsole zeigt nur Schlüssel-/STS-Anmeldung an. Auch die technische
OIDC-Anwendung erhält die aktive Gruppenbindung zu `rustfs-admins`.

`meta_hide: true` versteckt nur die technische Kachel für normale Nutzer.
Authentik-Administratoren sehen sie weiterhin als Verwaltungsobjekt. Die
sichtbare Kachel bleibt ausschließlich `RustFS Console Access`.

Die produktive Konfiguration wurde direkt per Authentik-Shell angelegt. Die
spätere zentrale Einrichtungs-CLI muss Gruppen, beide Provider, Bindings,
Outpost-Zuordnung, Icon und das Verstecken der technischen Anwendung
idempotent reproduzieren.

Weiter mit [Erststart und Prüfung](erststart-und-pruefung.md).
