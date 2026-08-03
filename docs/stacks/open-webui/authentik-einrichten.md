# Authentik für Open WebUI einrichten

Dieses Dokument wird nach [Vorbereiten](vorbereiten.md) und vor dem ersten
Open-WebUI-Start durchgeführt. Open WebUI verwendet Authentik nativ per OIDC;
es gibt keinen lokalen Open-WebUI-Login und keinen Forward-Auth-Proxy.

## 1. Zugriffsgruppen prüfen

Navigation:

```text
Directory → Groups
```

Folgende Gruppen müssen vorhanden sein:

```text
openwebui-users
openwebui-admin
```

Für die Ersteinrichtung das verwendete Administratorkonto zu
`openwebui-admin` hinzufügen. Mitglieder von `openwebui-users` erhalten in
Open WebUI die Rolle `user`, Mitglieder von `openwebui-admin` die Rolle `admin`.

## 2. Rollen-Scope-Mapping anlegen

Navigation:

```text
Customization → Property Mappings → Create → OAuth2/OpenID Provider Scope Mapping
```

Falls noch nicht vorhanden, das Mapping anlegen:

```text
Name: Open WebUI Rollen
Scope name: roles
Expression:
```

```python
roles = []
if ak_is_group_member(request.user, name="openwebui-users"):
    roles.append("user")
if ak_is_group_member(request.user, name="openwebui-admin"):
    roles.append("admin")
return {"roles": roles}
```

Nur Gruppenmitglieder erhalten mindestens eine Rolle. Die Rolle `admin` wird
von Open WebUI als Administratorrolle ausgewertet.

## 3. Anwendung und OIDC-Provider anlegen

Navigation:

```text
Applications → Applications → Create with Provider
```

### Anwendung

```text
Name: Open WebUI
Slug: open-webui
Group: KI
Policy engine mode: ANY
Launch URL: https://webui.<DOMAIN>
```

### OAuth2/OpenID Provider

Die Formularfelder in der angezeigten Reihenfolge ausfüllen:

#### Provider Name

```text
Open WebUI OIDC Provider
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

Unter **Redirect URIs / Origins** zwei Einträge hinzufügen:

| Modus | Typ | URL |
|---|---|---|
| Strict | Authorization | `https://webui.<DOMAIN>/oauth/oidc/callback` |
| Strict | Post Logout | `https://webui.<DOMAIN>/` |

`Regex` nicht verwenden: Es würden damit mehr Rückleitungsadressen als nötig
akzeptiert.

#### Advanced flow settings

```text
Authentication Flow: leer lassen
Invalidation Flow: default-provider-invalidation-flow (Logged out of application)
```

`default-source-authentication` ist ein Flow für externe Benutzerquellen und
darf hier nicht ausgewählt werden.

#### Advanced protocol settings

Folgende Standardwerte beibehalten:

```text
Access Code Validity: minutes=1
Access Token Validity: minutes=5
Refresh Token Validity: days=30
Refresh Token Threshold: hours=1
Encryption Key: leer
Subject Mode: Based on the User's hashed ID
Include claims in id_token: An
Issuer mode: Each provider has a different issuer, based on the application slug
```

Bei **Scope** diese vier Einträge auswählen:

```text
authentik default OAuth Mapping: OpenID 'openid'
authentik default OAuth Mapping: OpenID 'email'
authentik default OAuth Mapping: OpenID 'profile'
Open WebUI Rollen
```

#### Machine-to-Machine authentication settings

```text
Federated OIDC Sources: leer
Federated OAuth2/OpenID Providers: leer
```

Anwendung und Provider speichern und verbinden. Zum Abrufen der Zugangsdaten
den gespeicherten Provider `Open WebUI OIDC Provider` über **Edit** erneut
öffnen. Dort stehen `Client ID` und `Client Secret`. Beide Werte in
`Compose/open-webui/.env` als `OPENWEBUI_OIDC_CLIENT_ID` beziehungsweise
`OPENWEBUI_OIDC_CLIENT_SECRET` eintragen. Das Secret nicht in die Dokumentation
oder in Git übernehmen.

## 4. Gruppenbindungen eintragen

An der Anwendung `Open WebUI` diese Bindings anlegen:

| Gruppe | Order | Enabled | Negate | Timeout | Failure result |
|---|---:|---|---|---:|---|
| `openwebui-admin` | 0 | Ja | Nein | 30 | fail |
| `openwebui-users` | 10 | Ja | Nein | 30 | fail |

Mit `Policy engine mode: ANY` reicht eine der beiden Gruppen.

## 5. Lokalen Open-WebUI-Signierschlüssel erzeugen

```bash
cd <PROJEKT_ROOT>/Compose/open-webui

openssl rand -base64 48 \
  | tr -d '\n' \
  > secrets/openwebui_secret_key

chmod 600 secrets/openwebui_secret_key

stat -c '%A %s Bytes %n' secrets/openwebui_secret_key
git check-ignore -v .env secrets/openwebui_secret_key
```

Erwartet: `-rw-------` und passende `.gitignore`-Regeln. Der Schlüssel bleibt
über Neustarts erhalten; er wird nicht in Git eingecheckt.

Weiter mit [Erststart und Prüfung](erststart-und-pruefung.md).
