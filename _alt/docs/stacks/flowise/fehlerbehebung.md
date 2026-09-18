# Flowise-Stack: Fehlerbehebung

## Authentik meldet `Redirect URI Error` oder `invalid_request`

Beim Provider **Flowise Access Provider** prüfen:

- External host: `https://flowise.<DOMAIN>/`
- beide Callback-URIs aus [Authentik einrichten](authentik-einrichten.md)
- Grant-Types: `authorization_code`, `client_credentials`, `password`
- Outpost-Zuordnung und Gruppenbindung zu `flowise-users`

Nach einer Provider-Korrektur Browser-Cookies für `auth.<DOMAIN>` und
`flowise.<DOMAIN>` löschen oder ein privates Fenster verwenden. Ein vor der
Korrektur erzeugter OAuth-State bleibt ungültig.

## Flowise startet nicht oder ist nicht healthy

```bash
cd <PROJEKT_ROOT>/Compose/flowise
docker compose ps
docker compose logs --tail=150 flowise flowise-postgresql
```

Der Healthcheck lautet `http://127.0.0.1:3000/api/v1/ping` und muss `pong`
liefern. Bei Schreibfehlern im Datenverzeichnis Eigentümer des externen
Volumes auf `1000:1000` setzen.

## ReActAgentChat und ReActAgentLLM werden beim Start nicht geladen

Flowise `3.1.3` protokolliert derzeit beim Laden dieser zwei ReAct-Nodes einen
`ERR_PACKAGE_PATH_NOT_EXPORTED` für `@langchain/core/utils/uuid`. Der übrige
Node-Katalog, Datenbankmigrationen und Serverstart sind davon nicht betroffen;
die beiden ReAct-Nodes stehen jedoch nicht zur Verfügung. Vor einem
Versionswechsel Release Notes und einen Test in einer separaten Instanz
prüfen, statt den Produktivstack blind hoch- oder herunterzustufen.

## Qdrant oder Neo4j aus einem Node nicht erreichbar

Nur die internen Adressen verwenden und die jeweiligen Zugangsdaten als
Flowise-Credential speichern. Der Container muss Mitglied von
`qdrant_clients` beziehungsweise `neo4j_clients` sein. Öffentliche URLs
führen über Authentik und sind für diese Maschinenverbindungen ungeeignet.
