# Open-WebUI-Stack: Erststart und Prüfung

Für die Standardkonfiguration mit OIDC müssen [Vorbereiten](vorbereiten.md)
und [Authentik einrichten](authentik-einrichten.md) abgeschlossen sein. Für
die Alternative mit lokalen Konten gilt stattdessen der eigene Abschnitt
[Erststart ohne OIDC](#alternative-erststart-ohne-oidc).

## 1. Lokale Konfiguration prüfen

```bash
cd <PROJEKT_ROOT>/Compose/open-webui

test -s secrets/openwebui_secret_key \
  || { echo 'Fehlt oder leer: secrets/openwebui_secret_key' >&2; exit 1; }
test -n "$(sed -n 's/^OPENWEBUI_OIDC_CLIENT_ID=//p' .env)" \
  || { echo 'Fehlt: OPENWEBUI_OIDC_CLIENT_ID in .env' >&2; exit 1; }
test -n "$(sed -n 's/^OPENWEBUI_OIDC_CLIENT_SECRET=//p' .env)" \
  || { echo 'Fehlt: OPENWEBUI_OIDC_CLIENT_SECRET in .env' >&2; exit 1; }

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
```

Erwartet:

- HTTP liefert einen `308`-Redirect zu HTTPS.
- HTTPS liefert die Open-WebUI-Anmeldeseite. Die Schaltfläche beziehungsweise
  die automatische Weiterleitung führt zur Authentik-Anmeldung.

Zertifikat prüfen:

```bash
openssl s_client \
  -connect webui.<DOMAIN>:443 \
  -servername webui.<DOMAIN> \
  </dev/null 2>/dev/null \
  | openssl x509 -noout -subject -issuer -dates
```

## 5. OIDC-Anmeldung und Rollen prüfen

In einem privaten Browserfenster `https://webui.<DOMAIN>` öffnen.

1. Mit einem Authentik-Konto aus `openwebui-admin` anmelden.
2. Authentik leitet zur Open-WebUI-Startseite zurück.
3. Unter Open WebUI → Admin Panel → Users prüfen, dass das Konto die Rolle
   `admin` erhalten hat.

Danach mit einem Mitglied von `openwebui-users` anmelden und die Rolle `user`
prüfen. Ein Benutzer ohne eine dieser Gruppen darf durch Authentik nicht zur
Anwendung autorisiert werden.

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

## Alternative: Erststart ohne OIDC

Für die in [Ohne OIDC einrichten](authentik-einrichten-ohne-oidc.md)
beschriebene Forward-Auth-Variante alle Compose-Befehle mit dem Override
ausführen:

```bash
test -s secrets/openwebui_secret_key \
  || { echo 'Fehlt oder leer: secrets/openwebui_secret_key' >&2; exit 1; }
docker compose -f compose.yml -f compose.local-auth.yml config --quiet
docker compose -f compose.yml -f compose.local-auth.yml pull
docker compose -f compose.yml -f compose.local-auth.yml up -d
docker compose -f compose.yml -f compose.local-auth.yml ps
```

`https://webui.<DOMAIN>` führt dann zunächst durch Authentik und zeigt danach
den lokalen Open-WebUI-Login. Der erste lokale Benutzer wird Administrator.
