# Authentik für Jellyfin einrichten

Jellyfin wird ausschließlich im Browser verwendet. Authentik Forward Auth
schützt deshalb die gesamte öffentliche Adresse, bevor Jellyfin seine eigene
lokale Benutzeranmeldung anzeigt.

## 1. Zugriffsgruppe anlegen

Navigation:

```text
Directory → Groups → Create
```

```text
Name: jellyfin-users
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
Name: Jellyfin Access
Slug: jellyfin-access
Group: Medien
Policy engine mode: ANY
Launch URL: https://jellyfin.<DOMAIN>/
```

`Medien` ist nur die organisatorische Gruppe im Authentik-Dashboard. Falls sie
noch nicht existiert, dort anlegen; den tatsächlichen Zugriff begrenzt erst die
folgende Gruppenbindung.

Weiter mit **Choose a Provider**.

### Configure Provider

#### Provider Name

```text
Jellyfin Access Provider
```

#### Authorization Flow

```text
default-provider-authorization-implicit-consent
```

#### Protocol settings

```text
Mode: Forward auth (single application)
External host: https://jellyfin.<DOMAIN>
```

Alle übrigen Felder auf den Standardwerten lassen.

## 3. Configure Bindings

Eine Gruppenbindung hinzufügen:

```text
Group: jellyfin-users
Order: 0
Enabled: Ja
Negate: Nein
Timeout: 30
Failure result: fail
```

Anwendung erstellen und den Provider dem **authentik Embedded Outpost**
zuordnen. Bei Forward Auth ist kein `Internal Host` erforderlich.

Weiter mit [Erststart und Prüfung](erststart-und-pruefung.md).
