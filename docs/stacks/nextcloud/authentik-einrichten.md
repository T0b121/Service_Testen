# Authentik für Nextcloud und ONLYOFFICE einrichten

Nextcloud meldet Benutzer nativ per OpenID Connect (OIDC) bei Authentik an.
ONLYOFFICE erhält weiterhin einen separaten Forward-Auth-Provider, weil der
Document Server kein Benutzer-SSO benötigt.

## Zugriffsgruppe

In Authentik anlegen:

```text
Directory → Groups → Create
Name: nextcloud-users
```

Alle berechtigten Personen dieser Gruppe hinzufügen.

Für zentral verwaltete Nextcloud-Administratoren zusätzlich anlegen:

```text
Directory → Groups → Create
Name: nextcloud-admins
```

Mitglieder von `nextcloud-admins` müssen ebenfalls Mitglied von
`nextcloud-users` sein. Die erste Gruppe steuert den Zugang, die zweite die
zusätzlichen Administratorrechte innerhalb von Nextcloud.

## Gruppen-Claim für Nextcloud

In Authentik unter **Customisation → Property mappings → Create → Scope
Mapping** einen Scope Mapping mit diesen Werten anlegen:

```text
Name: Nextcloud OAuth Mapping: groups
Scope name: nextcloud-groups
```

Als Expression eintragen:

```python
groups = []

if request.user.groups.filter(name="nextcloud-users").exists():
    groups.append("nextcloud-users")

if request.user.groups.filter(name="nextcloud-admins").exists():
    groups.append("admin")

return {"nextcloud_groups": groups}
```

`admin` ist absichtlich der Name der eingebauten Nextcloud-Administratorgruppe.
So bleibt die Entscheidung, wer Nextcloud administrieren darf, in Authentik.

## Nextcloud-OIDC-Provider

In Authentik erstellen:

```text
Applications → Applications → Create with Provider
Application name: Nextcloud
Slug: nextcloud
Launch URL: https://cloud.<DOMAIN>/
Provider type: OAuth2/OpenID Provider
Client type: Confidential
Authorization flow: default-provider-authorization-implicit-consent
Grant type: Authorization Code
Redirect URI: https://cloud.<DOMAIN>/apps/user_oidc/code
Selected scopes: openid, profile, nextcloud-groups
Include claims in id_token: enabled
```

Den Scope Mapping `Nextcloud OAuth Mapping: groups` dazu bei **Selected scopes**
hinzufügen. Falls E-Mail-Adressen in Authentik nicht für alle Benutzer gepflegt
sind, den Standard-Scope `email` nicht auswählen.

Eine Binding-Regel für `nextcloud-users` erstellen. Damit erhalten nur diese
Mitglieder einen Autorisierungscode. Der OIDC-Provider wird **nicht** dem
Authentik Embedded Outpost zugeordnet.

Nach dem Speichern Client-ID und Client-Secret nur für die folgende
Nextcloud-Konfiguration bereithalten. Das Discovery-Dokument lautet:

```text
https://auth.<DOMAIN>/application/o/nextcloud/.well-known/openid-configuration
```

## ONLYOFFICE-Provider

Zusätzlich einen zweiten Provider erstellen:

```text
Application name: ONLYOFFICE Access
Slug: onlyoffice-access
Launch URL: https://office.<DOMAIN>/
Provider type: Proxy Provider
Mode: Forward auth (single application)
External host: https://office.<DOMAIN>
```

Diesen Provider auf `nextcloud-users` beschränken und dem eingebetteten
Outpost zuordnen. Die öffentliche Office-Adresse ist damit nicht anonym
erreichbar. Die internen URLs umgehen Traefik nur im isolierten Docker-Netz.

Weiter mit [Erststart und Prüfung](erststart-und-pruefung.md).
