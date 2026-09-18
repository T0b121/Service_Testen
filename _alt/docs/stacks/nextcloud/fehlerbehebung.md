# Nextcloud-Stack: Fehlerbehebung

## OIDC-Anmeldung leitet nicht zu Authentik weiter

Prüfen:

- Die App **OpenID Connect user backend** ist aktiviert.
- Der Discovery-Endpunkt lautet
  `https://auth.<DOMAIN>/application/o/nextcloud/.well-known/openid-configuration`.
- Client-ID, Client-Secret und Redirect-URI
  `https://cloud.<DOMAIN>/apps/user_oidc/code` stimmen mit Authentik überein.
- Der Benutzer ist Mitglied von `nextcloud-users`.
- Der Anwendungsbereich lautet `openid profile nextcloud-groups` und die
  Gruppen-Zuordnung `nextcloud_groups`.

Wenn die OIDC-Anmeldung als Standard eingerichtet wurde und nicht funktioniert,
per SSH in das Stack-Verzeichnis wechseln und den lokalen Bootstrap-Zugang
vorübergehend wieder aktivieren:

```bash
cd <PROJEKT_ROOT>/Compose/nextcloud
docker compose exec -u www-data nextcloud php occ config:app:set \
  --type=string --value=1 user_oidc allow_multiple_user_backends
docker compose exec -u www-data nextcloud php occ user:enable admin
docker compose exec -u www-data nextcloud php occ user:info admin
```

Die Ausgabe muss `enabled: true` enthalten. Bei PostgreSQL kann `user:enable`
nach der bereits erfolgreichen Statusänderung die Meldung
`savepoint "doctrine_2" does not exist` ausgeben. In diesem Fall nicht
blind wiederholen, sondern zuerst `user:info admin` prüfen. Zeigt es
`enabled: true`, ist der Zugang bereits wieder aktiviert.

Nach der Korrektur den OIDC-Login testen und den lokalen Zugang wieder
abschalten:

```bash
docker compose exec -u www-data nextcloud php occ config:app:set \
  --type=string --value=0 user_oidc allow_multiple_user_backends
docker compose exec -u www-data nextcloud php occ user:disable admin
docker compose exec -u www-data nextcloud php occ user:info admin
```

Die letzte Ausgabe muss wieder `enabled: false` enthalten.

## OIDC-Login meldet „Anmeldung verboten“

Die Gruppen-Whitelist-RegEx in der Nextcloud-App muss ohne äußere
Schrägstriche eingetragen werden:

```text
^(nextcloud-users|admin)$
```

`/^(nextcloud-users|admin)$/` ist falsch; die App fügt die Begrenzungszeichen
selbst hinzu und protokolliert dann `preg_match(): Unknown modifier`.

Prüfen, dass **Eindeutige Benutzer-ID verwenden** und **Anbieterkennung als
Präfix für IDs verwenden** deaktiviert sind. Beide Optionen würden die
Gruppen-ID `admin` verändern und damit die zentrale Administratorzuordnung
verhindern.

## OIDC-Administrator hat keine Nextcloud-Administrationsrechte

In Authentik muss das Scope Mapping für Mitglieder von `nextcloud-admins` den
Wert `admin` im Claim `nextcloud_groups` liefern. Anschließend ab- und wieder
anmelden und prüfen:

```bash
docker compose exec -u www-data nextcloud php occ group:info admin
```

Der OIDC-Benutzer muss dort als Mitglied erscheinen. Eine manuelle
`occ group:adduser`-Zuordnung ist in dieser Konfiguration nicht erforderlich.

## ONLYOFFICE-Menü fehlt oder die Datei wird nur heruntergeladen

Die ONLYOFFICE-App begrenzt den Editorzugriff über ihre eigene Gruppenliste.
Nach einer anfänglichen OIDC-Konfiguration mit gehashten Gruppen-IDs kann dort
noch eine alte, nicht mehr passende Gruppe gespeichert sein. Die erlaubte
Gruppe eindeutig setzen:

```bash
docker compose exec -u www-data nextcloud php occ config:app:set \
  onlyoffice groups --value='["nextcloud-users"]'
docker compose exec -u www-data nextcloud php occ config:app:get \
  onlyoffice groups
```

Danach die Dateien-Seite mit `Strg+F5` neu laden und für eine DOCX-, XLSX- oder
PPTX-Datei das Drei-Punkte-Menü öffnen. Dort muss **In ONLYOFFICE öffnen**
erscheinen. Ein normaler Klick darf weiterhin einen Download auslösen und ist
kein Verbindungsfehler.

## `office.<DOMAIN>` ist ohne Anmeldung sichtbar

Prüfen, ob der ONLYOFFICE-Provider in Authentik dem eingebetteten Outpost
zugeordnet ist und ob `nextcloud-users` eine Binding-Regel besitzt:

```bash
curl -I https://office.<DOMAIN>/
docker compose logs --tail=100 onlyoffice
```

Ohne Authentik-Sitzung ist eine `302`-Weiterleitung erwartet, kein `200`.

## ONLYOFFICE kann Nextcloud nicht erreichen

Die internen Adressen müssen exakt `http://onlyoffice/` und
`http://nextcloud/` lauten. Prüfen:

```bash
docker compose exec -u www-data nextcloud php occ config:system:get allow_local_remote_servers
docker compose exec onlyoffice curl --fail --silent http://nextcloud/status.php
```

Der Konfigurationswert muss `true` sein. JWT-Secret und Header
`AuthorizationJwt` müssen auf beiden Seiten identisch sein.

## Jellyfin sieht neue Uploads nicht

In Nextcloud prüfen, ob `/Jellyfin` auf `/mnt/jellyfin` zeigt. In Jellyfin die
Bibliothek `/media` anschließend scannen. Jellyfin liest das Volume nur;
Schreibzugriffe erfolgen ausschließlich über Nextcloud.

## Nextcloud bleibt beim Start ungesund

```bash
docker compose logs --tail=200 nextcloud nextcloud-postgresql nextcloud-redis
docker compose ps
```

Häufige Ursachen sind eine fehlende Secret-Datei, ein nicht vorhandenes
`jellyfin_media`-Volume oder ein nicht gesunder PostgreSQL-Dienst.
