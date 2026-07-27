# Core-Stack: Authentik einrichten

Diese Schritte werden nach dem ersten Containerstart aus [erststart-und-pruefung.md](erststart-und-pruefung.md) durchgeführt. Die Vorbereitung aus [vorbereiten.md](vorbereiten.md) muss bereits abgeschlossen sein.

## 1. Initial Setup

Öffnen:

```text
https://auth.<DOMAIN>/if/flow/initial-setup/
```

Einrichten:

- Standardadministrator `akadmin`
- starkes, einzigartiges Passwort
- erreichbare Administrationsadresse, sofern gewünscht
- Passwort sicher im Passwortmanager speichern

Ein zufälliges Passwort kann im Passwortmanager erzeugt werden oder lokal:

```bash
openssl rand -base64 24
```

Die Ausgabe direkt in einen Passwortmanager übernehmen. Nicht in eine Datei im Repository schreiben.

## 2. Admin-Oberfläche öffnen

Nach Anmeldung zur Administrationsoberfläche wechseln.

Die genaue Beschriftung kann sich innerhalb einer Versionslinie leicht ändern. Die benötigten Objekte bleiben:

```text
Application
Proxy Provider
Gruppenbindung
Embedded Outpost
```

## 3. Anwendung und Provider anlegen

Navigation:

```text
Applications → Applications
```

Neue Anwendung mit Provider erstellen.

### Anwendung

```text
Name: Traefik Dashboard
Slug: traefik-dashboard
Group: Core
```

### Provider

```text
Name: Traefik Dashboard Provider
Type: Proxy Provider
Authorization Flow: default-provider-authorization-implicit-consent (Authorize Application)
Mode: Forward auth (single application)
External host: https://proxy.<DOMAIN>
Token validity: hours=24
```

Für das interne Traefik-Dashboard wird bewusst `default-provider-authorization-implicit-consent` gewählt. Dieser Flow führt die Autorisierung ohne zusätzliche Zustimmungsseite des Benutzers aus.

Die zweite sichtbare Auswahl `default-provider-authorization-explicit-consent` enthält eine Consent-Stufe und fragt den Benutzer ausdrücklich, ob Daten an die Anwendung freigegeben werden dürfen. Sie ist sinnvoll, wenn diese Zustimmung bewusst angezeigt und protokolliert werden soll.

Eine Gegenüberstellung steht unter [Authentik verwalten: Provider-Authorization-Flows](authentik-verwaltung.md#provider-authorization-flows).

## 4. Zugriff auf Administratoren begrenzen

Eine Gruppenbindung anlegen:

```text
Group: authentik Admins
Enabled: true
Negate: false
Order: 0
Timeout: 30
Failure result: fail / nicht bestehen
```

Wichtig:

- Ohne Bindung kann eine Anwendung je nach Konfiguration für alle Benutzer sichtbar beziehungsweise zugänglich sein.
- Es ist nicht nötig, alle anderen Benutzer einzeln zu verbieten.
- Nur Mitglieder von `authentik Admins` bestehen diese Bindung.

## 5. Anwendung speichern

Kontrollieren:

```text
Application: Traefik Dashboard
Provider: Traefik Dashboard Provider
Authorization Flow: default-provider-authorization-implicit-consent
Mode: Forward auth (single application)
External host: https://proxy.<DOMAIN>
Token validity: hours=24
```

## 6. Embedded Outpost zuordnen

Navigation:

```text
Applications → Outposts
→ authentik Embedded Outpost
→ Edit
```

Im Bereich Anwendungen:

1. `Traefik Dashboard` bei verfügbaren Anwendungen auswählen.
2. mit dem einzelnen Pfeil in die ausgewählten Anwendungen verschieben.
3. speichern.

Danach muss der Provider beim Embedded Outpost erscheinen:

```text
Traefik Dashboard Provider
```

Der Outpost sollte gesund sein.

## 7. Zugang prüfen

In der Anwendung beziehungsweise im Provider die Zugangsprüfung öffnen.

Erwartet:

```text
akadmin: erlaubt
ak-outpost-...: nicht erlaubt
```

Dass der technische Outpost-Benutzer die Admin-Gruppenbindung nicht besteht, ist normal.

## 8. Outpost-Ping

```bash
curl -k -I \
  https://auth.<DOMAIN>/outpost.goauthentik.io/ping
```

Erwartet:

```text
HTTP/2 204
```

## 9. Dashboard testen

Privates Browserfenster:

```text
https://proxy.<DOMAIN>/dashboard/
```

Erwartet:

1. Authentik-Anmeldeseite
2. Anmeldung als Administrator
3. Rückleitung auf die Proxy-Domain
4. Traefik-Dashboard

## 10. Zugriff eines normalen Benutzers testen

Unter [Authentik verwalten: Internen Benutzer oder Testbenutzer anlegen](authentik-verwaltung.md#internen-benutzer-oder-testbenutzer-anlegen) einen Benutzer vom Typ `Internal User` anlegen. Dieser Testbenutzer darf nicht Mitglied von `authentik Admins` sein.

Mit diesem Benutzer im privaten Browserfenster anmelden.

Erwartet:

```text
Zugriff verweigert
```

## 11. Warum der Outpost-Router erforderlich ist

Beim Single-Application-Forward-Auth muss die geschützte Anwendungsdomain diesen Pfad an den Outpost weiterleiten:

```text
/outpost.goauthentik.io/
```

Für das Dashboard gilt daher:

```text
proxy.<DOMAIN>/dashboard/                  → Traefik api@internal
proxy.<DOMAIN>/outpost.goauthentik.io/    → Authentik Server
```

Der Outpost-Router darf nicht selbst erneut durch dieselbe Forward-Auth-Middleware geschützt werden.

## 12. MFA

MFA ist für den ersten Staging-Test nicht technisch zwingend, wird aber für alle Administratoren dringend empfohlen.

Details:

- [Authentik verwalten: MFA](authentik-verwaltung.md#mfa-für-administratoren)

## 13. Danach

Zurück zu:

- [Erststart und Prüfung](erststart-und-pruefung.md)

## Offizielle Referenzen

- [Authentik: Proxy Provider erstellen](https://docs.goauthentik.io/add-secure-apps/providers/proxy/create-proxy-provider/)
- [Authentik: Default Flows](https://docs.goauthentik.io/add-secure-apps/flows-stages/flow/examples/default_flows/)
- [Authentik: Consent Stage](https://docs.goauthentik.io/add-secure-apps/flows-stages/stages/consent/)
