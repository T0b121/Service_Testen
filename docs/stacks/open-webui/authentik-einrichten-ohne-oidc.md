# Authentik für Open WebUI ohne OIDC einrichten

Diese Alternative verwendet Authentik als äußeren Zugriffsschutz per Forward
Auth. Open WebUI verwaltet danach lokale Konten und Passwörter. Die
Standardkonfiguration des Stacks ist dagegen natives OIDC; die beiden Varianten
nicht gleichzeitig für dieselbe Installation verwenden.

## 1. Zugriffsgruppen prüfen

Unter `Directory → Groups` müssen diese Gruppen vorhanden sein:

```text
openwebui-users
openwebui-admin
```

Für die Ersteinrichtung das verwendete Authentik-Administratorkonto nur zur
Gruppe `openwebui-admin` hinzufügen.

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

### Provider

```text
Type: Proxy Provider
Name: Open WebUI Access Provider
Authorization flow: default-provider-authorization-implicit-consent
Mode: Forward auth (single application)
External host: https://webui.<DOMAIN>
```

## 3. Gruppenbindungen eintragen

In **Configure Bindings** diese Gruppenbindungen anlegen:

| Gruppe | Order | Enabled | Negate | Timeout | Failure result |
|---|---:|---|---|---:|---|
| `openwebui-admin` | 0 | Ja | Nein | 30 | fail |
| `openwebui-users` | 10 | Ja | Nein | 30 | fail |

Mit `Policy engine mode: ANY` genügt die Mitgliedschaft in einer der Gruppen.
Danach Anwendung und Provider absenden.

## 4. Embedded Outpost zuordnen

Navigation:

```text
Applications → Outposts → authentik Embedded Outpost → Edit
```

Die Anwendung `Open WebUI Access` zu den ausgewählten Anwendungen hinzufügen
und speichern. Das versionierte Compose-Override stellt den Outpost-Pfad unter
`/outpost.goauthentik.io/` bereit.

## 5. Start mit Compose-Override

Alle Compose-Befehle benötigen zusätzlich `compose.local-auth.yml`:

```bash
cd <PROJEKT_ROOT>/Compose/open-webui
docker compose -f compose.yml -f compose.local-auth.yml config --quiet
docker compose -f compose.yml -f compose.local-auth.yml up -d
```

Beim ersten Browser-Aufruf meldet sich der Benutzer zuerst bei Authentik an;
anschließend erscheint der lokale Open-WebUI-Login. Der erste lokale Benutzer
wird Open-WebUI-Administrator.
