# Authentik für Ollama einrichten

Diese Schritte richten den externen Zugriff auf `https://ollama.<DOMAIN>` ein.
Sie werden vor dem ersten öffentlichen Ollama-Test durchgeführt.

## 1. Gruppe anlegen

In Authentik unter **Directory → Groups** eine Gruppe anlegen:

```text
Name: ollama-users
```

Nur Benutzer hinzufügen, die die externe Ollama-API verwenden dürfen.

## 2. Anwendung und Proxy Provider anlegen

Unter **Applications → Applications** eine Anwendung erstellen:

```text
Name: Ollama API
Slug: ollama-api
Group: KI
Policy engine mode: ANY
Launch URL: https://ollama.<DOMAIN>
```

Als Provider einen **Proxy Provider** anlegen:

```text
Name: Ollama API Provider
Authorization flow: default-provider-authorization-implicit-consent
Mode: Forward auth (single application)
External host: https://ollama.<DOMAIN>
```

Die Anwendung mit diesem Provider verbinden.

## 3. Gruppenbindung erstellen

Bei der Anwendung eine Gruppenbindung eintragen:

```text
Group: ollama-users
Enabled: true
Negate: false
Order: 0
Timeout: 30
Failure result: fail / nicht bestehen
```

Danach Anwendung speichern.

## 4. Embedded Outpost zuordnen

Unter **Applications → Outposts** den **Authentik Embedded Outpost** öffnen.
Die Anwendung `Ollama API` bei den zugewiesenen Anwendungen ergänzen und
speichern.

## 5. Ersten berechtigten Benutzer zuordnen

Unter **Directory → Users** den vorgesehenen Benutzer, beispielsweise
`akadmin`, öffnen und zu `ollama-users` hinzufügen. Für den Negativtest bleibt
mindestens ein anderer Benutzer außerhalb dieser Gruppe.

## 6. Wichtige Einschränkung für externe Clients

Die äußere Absicherung verwendet Authentik Forward Auth. Nicht angemeldete
Browser erhalten eine Authentik-Anmeldung; danach funktionieren Browserzugriff
und Anfragen mit einer vorhandenen Authentik-Sitzung.

Der normale Ollama-Kommandozeilenclient führt keinen interaktiven
Authentik-Browser-Login durch. Ein automatisierter externer Client verwendet
später einen eigenen Service-Account und ein kurzlebiges Bearer-JWT, das der
vorhandene Proxy-Provider prüft. Die geplante Einrichtung und ein
Python-Beispiel stehen unter [Externe Python-API](externe-python-api.md).

Die API nicht durch eine Ausnahme in Traefik oder durch einen öffentlichen
Host-Port freigeben.

Weiter mit [Erststart und Prüfung](erststart-und-pruefung.md).
