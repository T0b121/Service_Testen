# Authentik für Uptime Kuma einrichten

Uptime Kuma besitzt kein natives OIDC. Authentik Forward Auth begrenzt daher
den Browserzugriff vor dem lokalen Uptime-Kuma-Login.

## 1. Zugriffsgruppe anlegen

Navigation:

```text
Directory → Groups → Create
```

```text
Name: uptime-kuma-users
```

Alle berechtigten Benutzer dieser Gruppe hinzufügen.

## 2. Anwendung und Proxy Provider anlegen

Navigation:

```text
Applications → Applications → Create with Provider
```

Bei **Create with Provider** `Create a new provider` und anschließend
`Proxy Provider` auswählen.

### Application

```text
Name: Uptime Kuma Access
Slug: uptime-kuma-access
Group: Betrieb
Policy engine mode: ANY
Launch URL: https://uptime.<DOMAIN>/
```

`Betrieb` ist hier ausschließlich die sichtbare Portal-Kategorie der
Anwendung, kein Authentik-Gruppenobjekt. Den tatsächlichen Zugriff begrenzt
allein die folgende Gruppenbindung zu `uptime-kuma-users`.

Weiter mit **Choose a Provider**.

### Configure Provider

#### Provider Name

```text
Uptime Kuma Access Provider
```

#### Authorization Flow

```text
default-provider-authorization-implicit-consent
```

#### Protocol settings

```text
Mode: Forward auth (single application)
External host: https://uptime.<DOMAIN>
```

Bei einer Erstellung in der Authentik-Oberfläche werden die beiden Callback-
Adressen aus dem `External host` automatisch erzeugt. Falls der Provider über
die Shell oder API wiederhergestellt wird, müssen sie unter **Redirect
URIs/Origins** explizit vorhanden sein:

```text
https://uptime.<DOMAIN>/outpost.goauthentik.io/callback?X-authentik-auth-callback=true
https://uptime.<DOMAIN>/?X-authentik-auth-callback=true
```

Für beide Einträge gilt:

```text
Matching mode: strict
Type: authorization
```

Als Grant Types sind mindestens `Authorization Code`, `Client credentials`
und `Password` aktiv. Alle übrigen Felder bleiben auf ihren Standardwerten.

## 3. Configure Bindings

Eine Gruppenbindung hinzufügen:

```text
Group: uptime-kuma-users
Order: 0
Enabled: Ja
Negate: Nein
Timeout: 30
Failure result: fail
```

Anwendung erstellen und den Provider dem **authentik Embedded Outpost**
zuordnen. Bei Forward Auth ist kein `Internal Host` erforderlich.

Die produktive Instanz wurde mit genau diesen Werten direkt in Authentik
angelegt. Eine spätere zentrale Einrichtungs-CLI muss dieselben Gruppen,
Providerwerte, Bindings und die Outpost-Zuordnung idempotent herstellen.

Weiter mit [Erststart und Prüfung](erststart-und-pruefung.md).
