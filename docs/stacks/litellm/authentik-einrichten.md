# Authentik für LiteLLM einrichten

LiteLLM verwendet für seine Admin-Oberfläche `/ui` natives OIDC. Der
OpenAI-kompatible API-Pfad `/v1` bleibt für Maschinenclients ohne
Browser-Weiterleitung erreichbar und prüft ausschließlich LiteLLM-Virtual-Keys.
LiteLLM dokumentiert Admin-UI-SSO seit Version 1.76.0 als kostenlos für bis zu
fünf Nutzer.

## 1. Zugriffsgruppe anlegen

Unter `Directory → Groups` diese Gruppen anlegen:

```text
litellm-users
litellm-admin
```

Normale Benutzer kommen in `litellm-users`; Administratorkonten zusätzlich in
`litellm-admin`.

## 2. Rollen-Scope-Mapping anlegen

Dieses Mapping übergibt die LiteLLM-Rolle direkt aus der Authentik-Gruppe. Es
ist für die Anmeldung allein nicht zwingend, verhindert aber einen manuellen
Rollenwechsel nach dem ersten Login.

Navigation:

```text
Customization → Property Mappings → Create → Scope Mapping
```

```text
Name: LiteLLM Rollen
Scope name: litellm_role
Expression:
```

```python
if ak_is_group_member(request.user, name="litellm-admin"):
    return {"litellm_role": "proxy_admin"}
if ak_is_group_member(request.user, name="litellm-users"):
    return {"litellm_role": "internal_user"}
return {}
```

## 3. Anwendung und OIDC-Provider anlegen

Navigation:

```text
Applications → Applications → Create with Provider
```

### Application

```text
Name: LiteLLM Administration
Slug: litellm
Group: KI
Policy engine mode: ALL
Launch URL: https://litellm.<DOMAIN>/ui
```

Weiter mit **Choose a Provider** und `OAuth2/OpenID Provider` auswählen.

### Configure Provider

Die Felder in der Reihenfolge der Authentik-Oberfläche ausfüllen.

#### Provider Name

```text
LiteLLM OIDC Provider
```

#### Authorization Flow

```text
default-provider-authorization-implicit-consent
```

#### Protocol settings

```text
Client Type: Confidential
Client ID: generierten Wert beibehalten
Client Secret: generierten Wert beibehalten
Grant Types: nur Authorization Code
Logout URI: leer
Signing Key: authentik Self-signed Certificate
```

Unter **Redirect URIs / Origins** einen Eintrag hinzufügen:

| Modus | Typ | URL |
|---|---|---|
| Strict | Authorization | `https://litellm.<DOMAIN>/sso/callback` |

#### Advanced flow settings

```text
Authentication Flow: leer / ----------
Invalidation Flow: default-provider-invalidation-flow (Logged out of application)
```

#### Advanced protocol settings

Die Standardwerte beibehalten. In der Scope-Tabelle mindestens diese
vorhandenen Scope Mappings aktivieren:

```text
openid
profile
email
litellm_role (LiteLLM Rollen)
```

`Subject Mode` bleibt bei `Based on the User's hashed ID`; LiteLLM verwendet
den stabilen Claim `sub` als Benutzerkennung. Die übrigen erweiterten und
Machine-to-Machine-Einstellungen bleiben unverändert.

## 4. Configure Bindings

Eine Gruppenbindung hinzufügen:

```text
Group: litellm-users
Order: 0
Enabled: Ja
Negate: Nein
Timeout: 30
Failure result: fail
```

Eine zweite Gruppenbindung anlegen:

```text
Group: litellm-admin
Order: 1
Enabled: Ja
Negate: Nein
Timeout: 30
Failure result: fail
```

`Policy engine mode` der Anwendung muss `ANY` sein, damit die Mitgliedschaft
in einer der beiden Gruppen genügt. Administratoren erhalten `proxy_admin`,
normale Mitglieder `internal_user`.

Anwendung und Provider erstellen. Es ist **keine** Outpost-Zuordnung nötig,
weil LiteLLM selbst OIDC nutzt und kein Authentik-Proxy-Provider verwendet.

## 5. Zugangsdaten in LiteLLM eintragen

Den gespeicherten Provider über **Edit** erneut öffnen. Dort die `Client ID`
und das `Client Secret` auslesen und in `Compose/litellm/.env` eintragen:

```dotenv
LITELLM_OIDC_CLIENT_ID=<CLIENT_ID>
LITELLM_OIDC_CLIENT_SECRET=<CLIENT_SECRET>
```

Das Secret bleibt ausschließlich in der lokalen `.env`.

Weiter mit [Erststart und Prüfung](erststart-und-pruefung.md).
