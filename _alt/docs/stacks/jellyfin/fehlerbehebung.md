# Jellyfin-Stack: Fehlerbehebung

## Öffentliche Seite liefert Jellyfin ohne Authentik-Anmeldung

Prüfen, ob `Jellyfin Access` dem **authentik Embedded Outpost** zugeordnet ist.
Der Traefik-Router benötigt das Middleware-Label `authentik@docker`.

```bash
cd <PROJEKT_ROOT>/Compose/jellyfin
docker compose up -d --force-recreate jellyfin
```

## Authentik zeigt nach dem Login „Not Found"

Im Proxy Provider muss `External host` exakt
`https://jellyfin.<DOMAIN>` lauten – ohne Pfad und ohne abschließenden Slash.
Danach Outpost-Zuordnung prüfen und den Browser-Login erneut starten.

## Jellyfin kann keine Medienbibliothek lesen

```bash
cd <PROJEKT_ROOT>/Compose/jellyfin
docker compose exec jellyfin sh -c 'ls -la /media && test -r /media'
```

Ein leeres Verzeichnis ist vor dem späteren Nextcloud-Setup erwartbar. Der
Mount ist absichtlich schreibgeschützt; `test -w /media` muss fehlschlagen.

## Transcoding ist langsam oder schlägt fehl

Der Stack verwendet zunächst CPU-Transcoding. In Jellyfin keine
Hardwarebeschleunigung aktivieren, solange kein `/dev/dri/renderD*` vorhanden
ist. Bei hoher Last direkte Wiedergabe bevorzugen oder die Client-Qualität
reduzieren.

## TCP 8096 ist am Host erreichbar

```bash
sudo ss -lntp | grep -E ':(8096)\s' || true
docker compose config
```

Die Compose-Datei darf nur `expose: 8096` enthalten, kein `ports:`-Mapping.

## Dienst startet nicht

```bash
cd <PROJEKT_ROOT>/Compose/jellyfin
docker compose ps
docker compose logs --tail=150 jellyfin
docker inspect --format '{{.State.Health.Status}}' jellyfin
```

Erwartet ist `healthy`. Das offizielle Jellyfin-Image prüft seinen
`/health`-Endpunkt selbst; zusätzliche HTTP-Client-Werkzeuge sind im Image
nicht zugesagt.
