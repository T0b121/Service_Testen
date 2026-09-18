# Ollama extern per Python-API verwenden

Diese Anleitung beschreibt die **spätere** Nutzung der bereits vorhandenen
Ollama-API von einem anderen System aus. Sie ändert weder den Ollama- noch den
Core-Stack und wird erst umgesetzt, wenn ein externer Client tatsächlich
benötigt wird.

Der Browserzugriff bleibt unverändert. Für einen nicht interaktiven Client wird
kein menschlicher Benutzer und kein Browser-Login verwendet, sondern ein
eigener Authentik-Service-Account mit einem zeitlich begrenzten Zugriffstoken.

## Zielarchitektur

```text
Externes Python-System
  |  1. Service-Account + App-Passwort
  v
Authentik: https://auth.<DOMAIN>/application/o/token/
  |  2. kurzlebiges JWT
  v
Traefik: https://ollama.<DOMAIN>/api/...
  |  3. Authorization: Bearer <JWT>
  v
Authentik Forward Auth prüft Gruppe und JWT
  v
Ollama:11434 im Docker-Netzwerk web
```

TCP 11434 bleibt dabei ohne Host-Port. Der externe Client verwendet
ausschließlich HTTPS auf `ollama.<DOMAIN>`.

Technische Grundlage sind die offizielle Authentik-Dokumentation zur
[M2M-Authentifizierung](https://docs.goauthentik.io/add-secure-apps/providers/oauth2/machine_to_machine/)
und zur [Bearer-Authentifizierung am Proxy-Provider](https://docs.goauthentik.io/add-secure-apps/providers/proxy/header_authentication/).

## Voraussetzungen

- Der [Ollama-Stack](uebersicht.md) läuft und mindestens ein Modell ist
  installiert.
- Der bestehende Authentik-Proxy-Provider `Ollama API Provider` und die Gruppe
  `ollama-users` sind wie unter [Authentik einrichten](authentik-einrichten.md)
  beschrieben vorhanden.
- Das externe System kann `https://auth.<DOMAIN>` und
  `https://ollama.<DOMAIN>` per HTTPS erreichen und vertraut dem
  Let's-Encrypt-Zertifikat.
- Python 3 und das Paket `requests` stehen auf dem externen System bereit.

Ein zukünftiger Open-WebUI-Container ist hiervon getrennt: Er kann innerhalb
des Docker-Netzwerks `web` weiterhin direkt `http://ollama:11434` verwenden.
Diese Anleitung gilt nur für Systeme außerhalb dieses Docker-Netzwerks.

## Spätere Einrichtung in Authentik

Die folgenden Schritte sind bewusst als Plan dokumentiert. Sie werden jetzt
nicht ausgeführt.

### 1. Bestehenden Proxy-Provider vorbereiten

In Authentik unter **Applications → Providers** den bestehenden Provider
`Ollama API Provider` öffnen.

- Unter **Authentication** die angezeigte `Client ID` notieren. Sie ist später
  die Variable `AUTHENTIK_CLIENT_ID` des Python-Clients.
- Unter **Header authentication** muss `Intercept header authentication`
  aktiviert sein. So verarbeitet der Proxy-Provider den Bearer-Token selbst,
  statt ihn an Ollama weiterzureichen.
- Die Gültigkeit von Zugriffstokens bewusst kurz halten, beispielsweise fünf
  Minuten. Bei einem Verlust ist ein Token damit nur begrenzt verwendbar.

Es wird dafür **kein zusätzlicher OAuth2-Provider** und kein öffentliches
Client-Secret angelegt. Authentik verwendet für diesen M2M-Ablauf die Client ID
des vorhandenen Proxy-Providers sowie ein App-Passwort des Service-Accounts.

### 2. Service-Account je externem System anlegen

Unter **Directory → Users** einen Benutzer vom Typ **Service account**
anlegen, beispielsweise:

```text
Username: ollama-python-system-a
Create Group: false
Expiring: true
Expires on: nach der lokalen Rotationsvorgabe, höchstens 90 Tage
```

Den bei der Erstellung einmalig angezeigten Wert sicher im Secret-Speicher des
externen Systems ablegen. Er ist das `AUTHENTIK_APP_PASSWORD`. Der
Service-Account erhält keine normale Benutzeranmeldung und repräsentiert keine
Person.

Unter **Directory → Groups** den Service-Account anschließend zu
`ollama-users` hinzufügen. Dadurch greift dieselbe Anwendungsbindung wie für
den Browserzugriff. Für jedes weitere externe System wird ein eigener
Service-Account mit eigenem App-Passwort angelegt.

### 3. Rotieren und entziehen

App-Passwörter werden unter **Directory → Tokens and App passwords** verwaltet.
Für eine Rotation:

1. Neues App-Passwort für genau diesen Service-Account erzeugen.
2. Das externe System auf den neuen Wert umstellen und testen.
3. Erst danach das alte App-Passwort löschen.

Bei einem Sicherheitsvorfall wird das betroffene App-Passwort sofort gelöscht
und der Service-Account nötigenfalls aus `ollama-users` entfernt. Bereits
ausgestellte Zugriffstokens bleiben höchstens bis zu ihrer kurzen Laufzeit
verwendbar.

## Konfiguration auf dem externen Python-System

Die Zugangsdaten gehören ausschließlich in den Secret-Speicher oder die
geschützte Laufzeitkonfiguration dieses Systems. Für einen lokalen Test kann
eine nicht versionierte Datei `.env` neben dem Python-Skript dienen:

```dotenv
# Öffentliche Adressen, ohne abschließenden Schrägstrich
AUTHENTIK_URL=https://auth.<DOMAIN>
OLLAMA_URL=https://ollama.<DOMAIN>

# Aus dem bestehenden Authentik-Provider, kein Provider-Secret
AUTHENTIK_CLIENT_ID=<CLIENT_ID_DES_OLLAMA_PROXY_PROVIDERS>

# Eigener Service-Account und dessen App-Passwort
AUTHENTIK_USERNAME=ollama-python-system-a
AUTHENTIK_APP_PASSWORD=<APP_PASSWORT>

# Muss bereits im Volume ollama_data installiert sein
OLLAMA_MODEL=qwen3:0.6b
```

Die Datei wird nicht eingecheckt und nur für den lokalen Test geschützt:

```bash
chmod 600 .env
```

In Produktion werden Secret-Manager, geschützte Umgebungsvariablen oder die
Secret-Funktion der jeweiligen Laufzeitumgebung verwendet. Zugangsdaten und
Tokens dürfen weder in Git noch in Tickets, Chats oder Anwendungslogs stehen.

## Python-Beispiel

Abhängigkeit installieren:

```bash
python3 -m pip install requests
```

Das Beispiel erwartet die oben genannten Umgebungsvariablen. Zum lokalen Laden
der `.env`-Datei kann die verwendete Laufzeit sie bereitstellen; das Skript
selbst liest absichtlich keine Secret-Datei ein.

```python
import os
import time

import requests


AUTHENTIK_URL = os.environ["AUTHENTIK_URL"].rstrip("/")
OLLAMA_URL = os.environ["OLLAMA_URL"].rstrip("/")
CLIENT_ID = os.environ["AUTHENTIK_CLIENT_ID"]
USERNAME = os.environ["AUTHENTIK_USERNAME"]
APP_PASSWORD = os.environ["AUTHENTIK_APP_PASSWORD"]
MODEL = os.environ["OLLAMA_MODEL"]


class OllamaClient:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.refresh_at = 0.0

    def _token(self):
        # Token vor Ablauf erneuern; kein Token wird auf die Platte geschrieben.
        if self.access_token and time.monotonic() < self.refresh_at:
            return self.access_token

        response = self.session.post(
            f"{AUTHENTIK_URL}/application/o/token/",
            data={
                "grant_type": "client_credentials",
                "client_id": CLIENT_ID,
                "username": USERNAME,
                "password": APP_PASSWORD,
                "scope": "profile",
            },
            timeout=15,
        )
        response.raise_for_status()

        payload = response.json()
        self.access_token = payload["access_token"]
        # Sicherheitsabstand, damit kein fast abgelaufenes Token versendet wird.
        self.refresh_at = time.monotonic() + max(
            int(payload.get("expires_in", 300)) - 30,
            1,
        )
        return self.access_token

    def chat(self, text):
        response = self.session.post(
            f"{OLLAMA_URL}/api/chat",
            headers={"Authorization": f"Bearer {self._token()}"},
            json={
                "model": MODEL,
                "messages": [{"role": "user", "content": text}],
                "stream": False,
            },
            # (Verbindungsaufbau, Modellantwort): Große Modelle brauchen Zeit.
            timeout=(15, 600),
        )
        response.raise_for_status()
        return response.json()["message"]["content"]


client = OllamaClient()
print(client.chat("Antworte ausschließlich mit OK."))
```

Die Anfrage an `POST /api/chat` und die Felder `model`, `messages` und
`stream` entsprechen der Ollama-API. `stream: false` sorgt dafür, dass das
Beispiel eine vollständige JSON-Antwort erhält. Für weitere Endpunkte dient die
offizielle [Ollama-API-Referenz](https://docs.ollama.com/api/) als Grundlage.

Das Python-Paket `requests` prüft das Serverzertifikat standardmäßig. Diese
Prüfung nicht mit `verify=False` abschalten.

## Verhalten und Tests nach der späteren Einrichtung

Ein gültiger Token führt zu einer normalen Ollama-Antwort. Authentik prüft
zuerst den Token und die Anwendungsberechtigung; danach entfernt es den
`Authorization`-Header, bevor die Anfrage Ollama erreicht. Ollama selbst muss
deshalb keine Zugangsdaten kennen.

| Ergebnis | Wahrscheinliche Ursache | Nächste Prüfung |
|---|---|---|
| `200` | Authentifizierung, Gruppenbindung und Ollama-Anfrage erfolgreich | Antwortinhalt und Modellname prüfen |
| `401` | Token fehlt, ist ungültig oder abgelaufen | Client ID, Service-Account und App-Passwort prüfen; Token neu beziehen |
| `403` | Service-Account ist nicht berechtigt | Mitgliedschaft in `ollama-users` und Anwendungsbindung prüfen |
| `302` zur Anmeldung | Bearer-Header fehlt oder der Provider verarbeitet Header-Authentifizierung nicht | `Intercept header authentication` des Proxy-Providers prüfen |
| `404` von Ollama | Modell ist nicht installiert oder API-Pfad falsch | Modell auf dem Server mit `ollama list` prüfen |
| TLS-Fehler | DNS, Zertifikatskette oder Systemzeit des externen Clients fehlerhaft | Zertifikat und Zeit auf dem Client prüfen |

Die Token-Ausstellung und die Modellanfrage sollten beim späteren ersten Test
separat geprüft werden. Dabei niemals den Token oder das App-Passwort ausgeben.

## Nicht verwenden

- Kein Host-Port `11434` und keine Netcup-Firewall-Regel dafür.
- Keine Traefik-Ausnahme für `/api/`.
- Kein normaler Authentik-Benutzer und kein persönliches Passwort im Skript.
- Kein geteilter Service-Account für mehrere fremde Systeme.
- Kein dauerhaft gespeicherter JWT; der Client fordert ihn bei Bedarf neu an.

Weiter mit [Betrieb](betrieb.md) und bei Problemen mit
[Fehlerbehebung](fehlerbehebung.md).
