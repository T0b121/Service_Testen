# Authentik für SearXNG einrichten

SearXNG selbst verwendet kein OIDC-Login. Ein Authentik Proxy Provider schützt
die gesamte öffentliche Oberfläche bereits in Traefik. Die interne JSON-API
bleibt ausschließlich für Container im Docker-Netzwerk erreichbar und läuft
nicht über Traefik.

## 1. Zugriffsgruppe anlegen

Navigation:

```text
Directory → Groups → Create
```

```text
Name: searxng-users
```

Alle berechtigten Benutzer dieser Gruppe hinzufügen.

## 2. Anwendung und Proxy Provider anlegen

Navigation:

```text
Applications → Applications → Create with Provider
```

Bei **Create with Provider** `Create a new provider` wählen und anschließend
`Proxy Provider` auswählen.

### Application

```text
Name: SearXNG Access
Slug: searxng-access
Group: Recherche
Policy engine mode: ANY
Launch URL: https://searxng.<DOMAIN>/
```

`Recherche` ist nur die organisatorische Gruppe im Authentik-Dashboard. Den
tatsächlichen Zugriff begrenzt später ausschließlich das Binding an
`searxng-users`.

Weiter mit **Choose a Provider**.

### Configure Provider

Die Felder in der Reihenfolge der Oberfläche ausfüllen.

#### Provider Name

```text
SearXNG Access Provider
```

#### Authorization Flow

```text
default-provider-authorization-implicit-consent
```

#### Protocol settings

```text
Mode: Forward auth (single application)
External host: https://searxng.<DOMAIN>
```

Alle übrigen Felder auf ihren Standardwerten lassen.

## 3. Configure Bindings

Eine Gruppenbindung hinzufügen:

```text
Group: searxng-users
Order: 0
Enabled: Ja
Negate: Nein
Timeout: 30
Failure result: fail
```

Anwendung erstellen und den Provider dem **authentik Embedded Outpost**
zuordnen. Bei Forward Auth ist kein `Internal Host` erforderlich.

Weiter mit [Erststart und Prüfung](erststart-und-pruefung.md).
