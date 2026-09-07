# Nextcloud-Stack: Übersicht

## Zweck

Nextcloud stellt private Dateiablage, Kalender, Kontakte und Zusammenarbeit
unter `https://cloud.<DOMAIN>` bereit. ONLYOFFICE bearbeitet insbesondere
Microsoft-Office-Dateien im Browser unter `https://office.<DOMAIN>`.
Nextcloud verwendet natives OpenID Connect (OIDC) gegen Authentik. ONLYOFFICE
wird separat durch Authentik Forward Auth geschützt.

## Vorausgesetzte Stacks

- [Core](../core/uebersicht.md): Traefik, TLS und Authentik
- [Jellyfin](../jellyfin/uebersicht.md): stellt das gemeinsame Volume
  `jellyfin_media` bereit

## Dienste

| Compose-Dienst | Container | Aufgabe | Öffentlich |
|---|---|---|---|
| `nextcloud` | `nextcloud` | Dateien, Kalender, Kontakte, WebDAV und Weboberfläche | über Traefik |
| `nextcloud-cron` | `nextcloud-cron` | Nextcloud-Hintergrundaufgaben | Nein |
| `nextcloud-postgresql` | `nextcloud-postgresql` | Nextcloud-Datenbank | Nein |
| `nextcloud-redis` | `nextcloud-redis` | Dateisperren und Cache | Nein |
| `onlyoffice` | `nextcloud-onlyoffice` | Browser-Editor für OOXML-Dateien | über Traefik |
| `jellyfin-media-permissions` | `nextcloud-jellyfin-media-permissions` | einmalige Schreibrechte für das Medienvolume | Nein |

## Endpunkte und Zugriffswege

| Zweck | Adresse | Schutz |
|---|---|---|
| Nextcloud | `https://cloud.<DOMAIN>` | natives Authentik-OIDC; Bootstrap-Admin wird nach dem Test deaktiviert |
| ONLYOFFICE im Browser | `https://office.<DOMAIN>` | Authentik Forward Auth und JWT zwischen Nextcloud und ONLYOFFICE |
| Nextcloud intern | `http://nextcloud/` | nur `nextcloud_internal` |
| ONLYOFFICE intern | `http://onlyoffice/` | nur `nextcloud_internal` |

Der Browser benötigt die öffentliche Office-Adresse für Editor und WebSocket.
Nextcloud und ONLYOFFICE verwenden für ihre gegenseitigen Serveranfragen
ausschließlich die internen Adressen. Dadurch erreicht ein anonymer Aufruf von
`office.<DOMAIN>` niemals den Document Server.

Die Nextcloud-Adresse hat bewusst keinen Traefik-Forward-Auth-Middleware.
Das verhindert doppelte Login-Flüsse und ermöglicht den offiziellen
Nextcloud-Desktop- und Mobil-Clients die native OIDC-Anmeldung. Die
Zugriffsregel liegt stattdessen im Authentik-OIDC-Provider.

## Netzwerke

| Netzwerk | Mitglieder | Zweck |
|---|---|---|
| `web` | Nextcloud, ONLYOFFICE | Traefik erreicht die beiden öffentlichen Ziele |
| `nextcloud_internal` | alle Stack-Dienste | Datenbank, Redis, interne Office-Anbindung und Medien-Hilfsdienst |

`nextcloud_internal` ist `internal: true`.

## Volumes

| Volume | Inhalt |
|---|---|
| `nextcloud_html` | Nextcloud-Code, Konfiguration, Apps und Daten |
| `nextcloud_postgresql_data` | Nextcloud-PostgreSQL |
| `nextcloud_redis_data` | Redis-Persistenz |
| `nextcloud_onlyoffice_*` | ONLYOFFICE-Daten, Logs, Laufzeitdaten, DB, Queue, Cache und Schriften |
| `jellyfin_media` | gemeinsame Medien; in Nextcloud schreibbar, in Jellyfin nur lesbar |

## Secrets

| Datei | Verwendet von |
|---|---|
| `secrets/postgresql_password` | Nextcloud und PostgreSQL |
| `secrets/nextcloud_admin_password` | einmalige Nextcloud-Initialisierung |
| `secrets/onlyoffice_jwt_secret` | ONLYOFFICE und die Nextcloud-ONLYOFFICE-App |

Weiter mit [Vorbereiten](vorbereiten.md).
