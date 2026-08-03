# Open-WebUI-Stack: Erststart und Prüfung

Vorher müssen [Vorbereiten](vorbereiten.md) und [Authentik einrichten](authentik-einrichten.md) abgeschlossen sein.

## 1. Lokale Konfiguration prüfen

```bash
cd <PROJEKT_ROOT>/Compose/open-webui

test -s secrets/openwebui_secret_key \
  || { echo 'Fehlt oder leer: secrets/openwebui_secret_key' >&2; exit 1; }

docker compose config --quiet
```

Erwartet: keine Ausgabe und Exit-Code `0`.

## 2. Image laden und starten

```bash
docker compose pull
docker compose up -d
docker compose ps
```

Nach dem Start soll `open-webui` den Status `healthy` erreichen. Der erste
Start kann wegen der Datenbankinitialisierung etwas länger dauern.

## 3. Interne Verbindung zu Ollama prüfen

```bash
docker compose exec open-webui \
  curl -fsS http://ollama:11434/api/tags
```

Erwartet ist eine JSON-Antwort. Ist bereits `qwen3:0.6b` im Ollama-Stack
installiert, enthält die Antwort dessen Modellnamen.

## 4. Öffentliche Adresse, Authentik und TLS prüfen

```bash
curl -I http://webui.<DOMAIN>
curl -I https://webui.<DOMAIN>
curl -I https://webui.<DOMAIN>/outpost.goauthentik.io/ping
```

Erwartet:

- HTTP liefert einen `308`-Redirect zu HTTPS.
- HTTPS leitet ohne vorhandene Authentik-Sitzung zur Authentik-Anmeldung.
- Der Outpost-Ping liefert `204`.

Zertifikat prüfen:

```bash
openssl s_client \
  -connect webui.<DOMAIN>:443 \
  -servername webui.<DOMAIN> \
  </dev/null 2>/dev/null \
  | openssl x509 -noout -subject -issuer -dates
```

## 5. Ersten lokalen Open-WebUI-Administrator anlegen

In einem privaten Browserfenster `https://webui.<DOMAIN>` öffnen.

1. Mit dem Authentik-Administratorkonto aus `openwebui-admin` anmelden.
2. Anschließend erscheint die lokale Open-WebUI-Anmeldeseite.
3. Ein lokales Konto mit eigener E-Mail-Adresse und starkem Passwort anlegen.

Der erste lokale Benutzer einer frischen Open-WebUI-Installation wird
automatisch Administrator. Open WebUI deaktiviert danach die Registrierung
automatisch; weitere lokale Konten werden vom Administrator verwaltet.

Erst nach erfolgreicher Anlage des lokalen Administrators weitere berechtigte
Benutzer in `openwebui-users` aufnehmen. Diese benötigen zusätzlich ein
freigegebenes lokales Open-WebUI-Konto.

Danach ein vorhandenes Modell, beispielsweise `qwen3:0.6b`, auswählen und
eine kurze Anfrage absenden.

## 6. Abschließende Prüfung

```bash
docker compose logs --since=15m open-webui
docker network inspect web
sudo ss -lntp | grep -E ':(8080)\s' || true
```

Erwartet:

- keine wiederkehrenden Start- oder Datenbankfehler,
- `open-webui` und `ollama` sind im Netzwerk `web`,
- TCP 8080 hat kein Host-Portmapping.

Weiter mit [Betrieb](betrieb.md).
