# Nextcloud-Stack: Erststart und Prüfung

Vorher müssen [Vorbereiten](vorbereiten.md) und
[Authentik einrichten](authentik-einrichten.md) abgeschlossen sein.

## Starten

```bash
cd <PROJEKT_ROOT>/Compose/nextcloud
docker compose pull
docker compose up -d
docker compose ps
docker compose logs --tail=100
```

Beim ersten Start erzeugt Nextcloud den lokalen Administrator. Der einmalige
Medien-Hilfsdienst muss mit Status `exited (0)` enden.

## Öffentlichen Zugriff prüfen

```bash
curl -I https://office.<DOMAIN>/outpost.goauthentik.io/ping
curl -I https://cloud.<DOMAIN>/
curl -I https://office.<DOMAIN>/
```

Der ONLYOFFICE-Outpost-Ping liefert `204`. Ohne Authentik-Sitzung leitet
`https://office.<DOMAIN>/` mit `302` zur Anmeldung weiter. Nextcloud zeigt
seine eigene Login-Seite; dort beginnt nach der OIDC-Einrichtung die
Weiterleitung zu Authentik.

## Nextcloud und ONLYOFFICE konfigurieren

1. `https://cloud.<DOMAIN>/` im privaten Browserfenster öffnen und zunächst
   mit dem lokalen Nextcloud-Administrator anmelden.
2. Unter **Apps** die App **OpenID Connect user backend** (`user_oidc`)
   aktivieren. Danach unter **Administration → OpenID Connect** einen Provider
   mit folgenden Werten anlegen:

   | Feld | Wert |
   |---|---|
   | Kennung | `authentik` |
   | Discovery-URI | `https://auth.<DOMAIN>/application/o/nextcloud/.well-known/openid-configuration` |
   | Client-ID | aus dem Authentik-OIDC-Provider |
   | Client-Secret | aus dem Authentik-OIDC-Provider |
   | Anwendungsbereich | `openid profile nextcloud-groups` |
   | Benutzerkennung | `sub` |
   | Anzeigename | `name` |
   | Gruppen-Zuordnung | `nextcloud_groups` |

   Die folgenden Felder bleiben leer: benutzerdefinierter Sitzungsendpunkt,
   Abmelde-URI, Extra Claims, E-Mail und alle weiteren optionalen
   Profilzuordnungen. **Verschachtelte und Fallback-Anspruchszuordnungen**
   bleibt deaktiviert.

   Unter **Authentifizierungs- und Zugriffskontrolleinstellungen** setzen:

   | Feld | Wert |
   |---|---|
   | Eindeutige Benutzer-ID verwenden | deaktiviert |
   | Anbieterkennung als Präfix für IDs verwenden | deaktiviert |
   | Gruppenbereitstellung verwenden | aktiviert |
   | Gruppen-Whitelist-RegEx | `^(nextcloud-users|admin)$` |
   | Anmeldung für Benutzer außerhalb der Whitelist beschränken | aktiviert |
   | Bearer-Token bei API- und WebDAV-Anfragen überprüfen | deaktiviert |

   Die Whitelist wird **ohne** umschließende Schrägstriche eingegeben. Die App
   setzt die regulären Ausdrucksbegrenzer selbst. Die deaktivierte eindeutige
   Benutzer-ID ist hier notwendig: Andernfalls hasht `user_oidc` auch die
   Gruppen-IDs und kann die echte Nextcloud-Gruppe `admin` nicht zuordnen.
   ID4me und **Store-login-token** bleiben deaktiviert.
3. In einem neuen privaten Browserfenster die OIDC-Anmeldung testen:

   - Ein Mitglied von `nextcloud-users` muss sich über Authentik anmelden
     können und wird beim ersten Login in Nextcloud angelegt.
   - Ein Mitglied von `nextcloud-admins` muss zusätzlich in der echten
     Nextcloud-Gruppe `admin` landen und die Administration sehen.

   Prüfen:

   ```bash
   docker compose exec -u www-data nextcloud php occ group:info admin
   ```

   Die Ausgabe muss beim OIDC-Administrator dessen Benutzer-ID unter den
   Mitgliedern der Gruppe `admin` zeigen. Es ist keine manuelle
   `occ group:adduser`-Zuordnung nötig.
4. Erst danach die OIDC-Anmeldung als Standard setzen und den nur für die
   Ersteinrichtung benötigten lokalen Bootstrap-Admin deaktivieren. Bei der
   dokumentierten `.env` lautet dessen Benutzername `admin`:

   ```bash
   docker compose exec -u www-data nextcloud php occ config:app:set \
     --type=string --value=0 user_oidc allow_multiple_user_backends
   docker compose exec -u www-data nextcloud php occ user:disable admin
   docker compose exec -u www-data nextcloud php occ user:info admin
   ```

   Die letzte Ausgabe muss `enabled: false` enthalten. Damit leitet die normale Nextcloud-Adresse immer zu Authentik weiter. Eine
   OIDC-Störung wird über SSH mit `occ` behoben; dafür ist kein lokaler Desktop
   am Server erforderlich. Die konkreten Wiederherstellungsbefehle stehen in
   der [Fehlerbehebung](fehlerbehebung.md).
5. Apps aktivieren: Calendar, Contacts, External storage support und ONLYOFFICE;
   bei Bedarf Deck, Talk, Forms, Collectives und Memories.
6. Unter **Administration → External storage** einen lokalen Speicher
   einrichten:

   | Feld | Wert |
   |---|---|
   | Ordnername | `Jellyfin` |
   | Externer Speicher | Local |
   | Konfiguration | `/mnt/jellyfin` |
   | Verfügbar für | `nextcloud-users` |

   Der Ordner erscheint danach in **Dateien** als `/Jellyfin`. Den
   Hintergrundmodus auf **Cron** setzen.
7. Lokale Serveradressen erlauben:

   ```bash
   docker compose exec -u www-data nextcloud php occ config:system:set \
     allow_local_remote_servers --value=true --type=boolean
   ```

8. In **Administration → ONLYOFFICE** die Serververbindung einrichten:

   | Feld | Wert |
   |---|---|
   | Dokumentserver-Adresse | `https://office.<DOMAIN>/` |
   | JWT-Secret | Inhalt von `secrets/onlyoffice_jwt_secret` |

   **Zertifikatsüberprüfung deaktivieren** und **Verbindung zu Demo ONLYOFFICE
   Docs Server herstellen** bleiben deaktiviert. Danach **Erweiterte
   Servereinstellungen** aufklappen und diese Werte setzen:

   | Feld | Wert |
   |---|---|
   | Authorization-Header | `AuthorizationJwt` |
   | Adresse von ONLYOFFICE Docs für interne Anforderungen vom Server | `http://onlyoffice/` |
   | Serveradresse für interne Anforderungen von ONLYOFFICE Docs | `http://nextcloud/` |

   Sind die erweiterten Einstellungen in einer anderen Connector-Version nicht
   vorhanden, die drei Werte einmalig per `occ` setzen:

   ```bash
   docker compose exec -u www-data nextcloud php occ config:app:set \
     onlyoffice DocumentServerInternalUrl --value='http://onlyoffice/'
   docker compose exec -u www-data nextcloud php occ config:app:set \
     onlyoffice StorageUrl --value='http://nextcloud/'
   docker compose exec -u www-data nextcloud php occ config:app:set \
     onlyoffice jwt_header --value='AuthorizationJwt'
   ```

   Die Browser-Adresse bleibt öffentlich, die beiden Server-zu-Server-
   Verbindungen bleiben dagegen im Docker-Netzwerk. Sie umgehen damit weder
   die Zugangskontrolle für Browser noch das JWT zwischen Nextcloud und
   ONLYOFFICE.

   Unter **Allgemeine Einstellungen** den Editorzugriff auf die Gruppe
   `nextcloud-users` begrenzen. Der Connector speichert diese Auswahl in seiner
   App-Konfiguration; prüfen und bei Bedarf eindeutig setzen:

   ```bash
   docker compose exec -u www-data nextcloud php occ config:app:set \
     onlyoffice groups --value='["nextcloud-users"]'
   docker compose exec -u www-data nextcloud php occ config:app:get \
     onlyoffice groups
   ```

   Für den Start: Zugriff auf externe Speicher nicht einschränken, erweiterte
   Zugriffsrechte deaktiviert lassen, Plugins und Makros deaktivieren sowie
   E-Mail-Benachrichtigungen ohne eingerichteten Mailversand deaktivieren.
   Dateivorschau, gleicher Browser-Tab, Metadaten je Version und
   Hintergrund-Verbindungsprüfung können aktiviert bleiben.

Die Browser-Adresse bleibt hinter Authentik; die Server-zu-Server-Verbindungen
bleiben im Docker-Netzwerk.

## ONLYOFFICE und Jellyfin verwenden

- Für ein Dokument, eine Tabelle oder Präsentation zunächst über **+ Neu** ein
  neues Textdokument, eine Tabelle oder Präsentation erzeugen. Alternativ eine
  `.docx`, `.xlsx` oder `.pptx`-Datei hochladen. Über das Drei-Punkte-Menü der
  Datei **In ONLYOFFICE öffnen** wählen. Ein einfacher Klick kann je nach
  Dateityp nur den Download starten. Änderungen im Editor speichern, schließen
  und die Datei erneut öffnen, um die Rückübertragung zu prüfen.
- Bilder, Videos oder Musik für Jellyfin direkt nach `/Jellyfin` hochladen,
  zum Beispiel nach `/Jellyfin/Fotos`, `/Jellyfin/Heimvideos und -bilder` oder
  `/Jellyfin/Filme`. ONLYOFFICE ist dafür nicht erforderlich.
- In Jellyfin die Bibliotheken getrennt einrichten: **Filme** auf
  `/media/Filme`, **Serien** auf `/media/Serien`, **Musik** auf `/media/Musik`
  und **Heimvideos und -bilder** auf `/media/Fotos` sowie
  `/media/Heimvideos und -bilder`. In dieser Jellyfin-Version gibt es keinen
  separaten Inhaltstyp für reine Fotos. Jellyfin hat auf dieses Volume nur
  Lesezugriff; Dateien werden ausschließlich über Nextcloud verändert.

## Abschlussprüfung

```bash
docker compose exec -u www-data nextcloud php occ status
docker compose exec onlyoffice curl --fail --silent http://localhost/healthcheck
docker compose exec -u www-data nextcloud test -w /mnt/jellyfin
```

Eine DOCX-, XLSX- und PPTX-Datei testweise öffnen, ändern, schließen und den
erneuten Download sowie die Version in Nextcloud prüfen. Zusätzlich ein Bild
oder eine Mediendatei nach `/Jellyfin` hochladen, die Jellyfin-Bibliothek
scannen und die Datei dort öffnen.

Weiter mit [Betrieb](betrieb.md).
