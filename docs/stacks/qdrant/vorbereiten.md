# Qdrant-Stack: Vorbereiten

Voraussetzung ist ein funktionierender [Core-Stack](../core/erststart-und-pruefung.md).

## Lokale `.env`

`Compose/qdrant/.env` ist absichtlich ignoriert und enthält:

```dotenv
DOMAIN=<DOMAIN>
QDRANT_VERSION=v1.19
QDRANT_API_KEY=<starker_lokaler_api_schluessel>
```

Qdrant hat für `QDRANT__SERVICE__API_KEY` keine native `*_FILE`-Variante.
Deshalb ist dies der dokumentierte Fallback: `.env` bleibt lokal, hat Modus
`0600` und wird nie eingecheckt.

```bash
cd <PROJEKT_ROOT>/Compose/qdrant
chmod 600 .env
stat -c '%A %n' .env
git check-ignore -v .env
docker compose config --quiet
```

## Netz

Der Stack verwendet das bestehende externe `web`-Netz für Traefik sowie das
interne Docker-Netz `qdrant_clients` für spätere KI-Clients. Es wird einmalig
angelegt:

```bash
docker network create --internal qdrant_clients
```

Der Befehl darf bei bereits vorhandenem Netz nicht erneut ausgeführt werden.

Weiter mit [Authentik einrichten](authentik-einrichten.md).
