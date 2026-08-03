# Open-WebUI-Stack: Fehlerbehebung

## 1. Standarddiagnose

```bash
cd <PROJEKT_ROOT>/Compose/open-webui

docker compose config --quiet
docker compose ps -a
docker compose logs --tail=200 open-webui
docker network inspect web
```

## 2. Container startet nicht oder ist nicht healthy

```bash
docker inspect open-webui --format '{{json .State.Health}}'
docker compose logs --tail=200 open-webui
stat -c '%A %s Bytes %n' secrets/openwebui_secret_key
```

Der Schlüssel muss vorhanden, nicht leer und `-rw-------` sein.

## 3. Authentik leitet nicht zu Open WebUI weiter

Prüfen:

- DNS für `webui.<DOMAIN>`,
- Proxy Provider `Open WebUI Access Provider`,
- Bindings der Anwendung `Open WebUI Access`,
- Zuweisung zum Authentik Embedded Outpost,
- Outpost-Pfad:

```bash
curl -I https://webui.<DOMAIN>/outpost.goauthentik.io/ping
```

Erwartet ist `204`.

## 4. Authentik meldet `Anfrage wurde verweigert`

Der Benutzer erfüllt keine Gruppenbindung. Mitgliedschaft in
`openwebui-users` oder `openwebui-admin` sowie `Policy engine mode: ANY`
prüfen. Danach neu anmelden.

## 5. Lokaler Open-WebUI-Login funktioniert nicht

Der lokale Login ist unabhängig von Authentik. Prüfen:

- das Konto existiert in Open WebUI,
- das Konto ist nicht `pending` oder deaktiviert,
- das Passwort ist korrekt,
- die Registrierung wurde nicht vor der Anlage des ersten Kontos manuell
  deaktiviert.

Der erste Benutzer einer frischen Installation ist der lokale Administrator.

## 6. Keine Modelle in Open WebUI

```bash
docker compose exec open-webui curl -fsS http://ollama:11434/api/tags

cd <PROJEKT_ROOT>/Compose/ollama
docker compose exec ollama ollama list
```

Beide Container müssen im Netzwerk `web` sein. `OLLAMA_BASE_URL` darf nicht
auf `localhost` oder die externe HTTPS-Adresse zeigen.

## 7. TCP 8080 ist am Host erreichbar

```bash
sudo ss -lntp | grep -E ':(8080)\s' || true
docker compose config
```

Die Compose-Datei darf nur `expose: 8080` enthalten, kein `ports:`-Mapping.

## 8. CORS-Warnung im Startprotokoll

`CORS_ALLOW_ORIGIN` muss auf die öffentliche Adresse begrenzt sein:

```yaml
CORS_ALLOW_ORIGIN: https://webui.<DOMAIN>
```

Nach einer Änderung den Container neu erstellen:

```bash
docker compose up -d --force-recreate open-webui
```
