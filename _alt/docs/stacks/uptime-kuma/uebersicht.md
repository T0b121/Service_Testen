# Uptime-Kuma-Stack: Übersicht

Uptime Kuma überwacht die Erreichbarkeit der vorhandenen Dienste. Das
Dashboard ist unter `https://uptime.<DOMAIN>` verfügbar, erhält keinen
Host-Port und ist vollständig durch Authentik Forward Auth geschützt.

Uptime Kuma bietet in der freien Version kein natives OIDC. Nach der
Authentik-Anmeldung ist deshalb zusätzlich der lokale Uptime-Kuma-Login
erforderlich. Dieser lokale Zugang verwaltet ausschließlich Monitore,
Benachrichtigungen und Statusseiten.

## Enthaltene Dienste

| Dienst | Zweck | Erreichbarkeit |
|---|---|---|
| Uptime Kuma | Überwachung, Benachrichtigungen und Statusseiten | Browser über `https://uptime.<DOMAIN>`; intern `http://uptime-kuma:3001` im Netzwerk `web` |

## Voraussetzungen

- Der [Core-Stack](../core/uebersicht.md) läuft einschließlich Traefik und
  Authentik.
- Die Wildcard-DNS-Einträge oder explizite A- und AAAA-Einträge für
  `uptime.<DOMAIN>` zeigen auf den Server.
- Berechtigte Benutzer sind in der Authentik-Gruppe `uptime-kuma-users`.

## Persistente Daten

| Volume | Inhalt |
|---|---|
| `uptime_kuma_data` | Embedded-MariaDB-Datenbank, Benutzer, Monitore, Benachrichtigungen und Einstellungen |

Uptime Kuma wurde mit der Datenbankoption **Embedded MariaDB** eingerichtet.
MariaDB läuft dabei ausschließlich innerhalb des Kuma-Containers und ist
weder als eigener Container noch über einen Host-Port erreichbar.

## Sicherheitsgrenzen

- Nur Traefik veröffentlicht Ports `80` und `443` am Host.
- Uptime Kuma veröffentlicht nur den internen Container-Port `3001` im
  Netzwerk `web`.
- Der Docker-Socket wird absichtlich **nicht** eingehängt. Container werden
  über HTTP-, TCP-, DNS-, Ping- oder andere Netzwerkmonitore überwacht, nicht
  durch direkten Zugriff auf die Docker-Engine.
- Öffentliche Statusseiten bleiben deaktiviert, solange sie nicht bewusst
  ohne Authentik veröffentlicht werden sollen.
- Die aktuellen Monitore greifen ausschließlich auf interne Docker-Adressen
  zu; sie umgehen weder Authentik für Browserzugriffe noch veröffentlichen sie
  zusätzliche Schnittstellen.

Weiter mit [Vorbereiten](vorbereiten.md).
