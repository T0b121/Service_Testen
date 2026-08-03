# Authentik für Open WebUI einrichten

Dieses Dokument wird nach [Vorbereiten](vorbereiten.md) und vor dem ersten
Open-WebUI-Start durchgeführt. Authentik schützt die öffentliche Adresse mit
einem Proxy Provider. Open WebUI verwendet zunächst einen eigenen lokalen
Login; der Authentik-Login ist die äußere Zugriffsschranke.

Der bereits angelegte Scope Mapping `Open WebUI Rollen` wird in diesem Zustand
noch nicht verwendet. Er kann für eine spätere native OIDC-Umstellung erhalten
bleiben.

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

Für die Ersteinrichtung das verwendete Administratorkonto ausschließlich zu
`openwebui-admin` hinzufügen. Noch keine weiteren Benutzer in eine dieser
Gruppen aufnehmen. Damit kann beim ersten lokalen Open-WebUI-Login niemand
zuvorkommen und das erste Konto anlegen.

## 2. Anwendung und Proxy Provider anlegen

Navigation:

```text
Applications → Applications → Create with Provider
```

### Anwendung

```text
Name: Open WebUI Access
Slug: open-webui-access
Group: KI
Policy engine mode: ANY
Launch URL: https://webui.<DOMAIN>
```

### Proxy Provider

Provider-Typ und Werte:

```text
Type: Proxy Provider
Name: Open WebUI Access Provider
Authorization flow: default-provider-authorization-implicit-consent
Mode: Forward auth (single application)
External host: https://webui.<DOMAIN>
```

Anwendung und Provider speichern und verbinden.

## 3. Gruppenbindungen eintragen

An der Anwendung `Open WebUI Access` diese Bindings anlegen:

| Gruppe | Order | Enabled | Negate | Timeout | Failure result |
|---|---:|---|---|---:|---|
| `openwebui-admin` | 0 | Ja | Nein | 30 | fail |
| `openwebui-users` | 10 | Ja | Nein | 30 | fail |

Mit `Policy engine mode: ANY` reicht eine der beiden Gruppen. Während der
Ersteinrichtung ist nur das Administratorkonto Mitglied von
`openwebui-admin`.

## 4. Embedded Outpost zuordnen

Navigation:

```text
Applications → Outposts → authentik Embedded Outpost → Edit
```

Die Anwendung `Open WebUI Access` zu den ausgewählten Anwendungen hinzufügen
und speichern.

Der versionierte Open-WebUI-Stack stellt später für diesen Provider die
Outpost-Route unter `/outpost.goauthentik.io/` bereit.

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
