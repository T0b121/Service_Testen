# Jellyfin-Stack: Erststart und Prüfung

Vorher müssen [Vorbereiten](vorbereiten.md) und
[Authentik einrichten](authentik-einrichten.md) abgeschlossen sein.

## 1. Image laden und starten

```bash
cd <PROJEKT_ROOT>/Compose/jellyfin
docker compose pull
docker compose up -d
docker compose ps
docker compose logs --tail=100 jellyfin
```

Der erste Start erzeugt die drei benannten Volumes. Der Dienst muss `Up` sein;
ein vorhandener Image-Healthcheck kann während der Initialisierung kurz
`starting` anzeigen.

## 2. Öffentlichen Zugriff und Authentik prüfen

```bash
curl -I https://jellyfin.<DOMAIN>/outpost.goauthentik.io/ping
curl -I https://jellyfin.<DOMAIN>/
```

Erwartet:

- der Outpost-Ping liefert `204`,
- der Aufruf von `/` liefert ohne Authentik-Sitzung `302` zur Anmeldung.

Danach `https://jellyfin.<DOMAIN>/` in einem privaten Browserfenster öffnen.
Ein Mitglied von `jellyfin-users` meldet sich zuerst bei Authentik an und
erreicht danach den Jellyfin-Einrichtungsassistenten. Ein Benutzer außerhalb
der Gruppe wird durch Authentik abgewiesen.

## 3. Jellyfin einrichten

1. Sprache auswählen.
2. Ein lokales Jellyfin-Administratorkonto mit starkem, eigenständigem
   Passwort anlegen.
3. Bei **Medienbibliothek hinzufügen** zunächst keine Bibliothek anlegen,
   solange `jellyfin_media` leer ist.
4. Remotezugriff aktiviert lassen: Die äußere Erreichbarkeit ist durch
   Traefik, HTTPS und Authentik begrenzt.
5. Assistent abschließen und mit dem lokalen Jellyfin-Konto anmelden.

Die Authentik- und Jellyfin-Anmeldung sind absichtlich getrennt. Das lokale
Jellyfin-Konto steuert später Bibliotheks- und Wiedergaberechte.

## 4. Medienvolume prüfen

```bash
docker volume inspect jellyfin_config jellyfin_cache jellyfin_media
docker compose exec jellyfin sh -c 'test -r /media && test ! -w /media'
```

Der zweite Befehl muss ohne Ausgabe mit Exit-Code `0` enden. Er bestätigt, dass
Jellyfin das gemeinsame Medienvolume lesen, aber nicht beschreiben kann.

Sobald der spätere Nextcloud-Stack Medien in `jellyfin_media` bereitstellt,
wird in Jellyfin eine Bibliothek mit dem Pfad `/media` angelegt und gescannt.

## 5. Abschließende Prüfung

```bash
cd <PROJEKT_ROOT>/Compose/jellyfin
docker compose logs --since=15m jellyfin
docker network inspect web
sudo ss -lntp | grep -E ':(8096)\s' || true
```

Erwartet:

- keine wiederkehrenden Startfehler,
- `jellyfin` ist im Netzwerk `web`,
- TCP 8096 besitzt kein Host-Portmapping.

Weiter mit [Betrieb](betrieb.md).
