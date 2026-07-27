# Serversicherheit

## 1. SSH

Empfohlen:

- Anmeldung mit SSH-Schlüsseln
- Passwortanmeldung deaktivieren, nachdem Schlüsselzugriff geprüft wurde
- direkter Root-Login deaktivieren
- mindestens eine zweite offene Testsitzung bei Firewall- oder SSH-Änderungen
- private Schlüssel mit Passphrase schützen
- nicht benötigte Benutzer entfernen oder sperren

Vor dem Schließen der aktuellen Sitzung immer eine zweite Anmeldung testen.

## 2. Firewall

- Standardrichtlinie für eingehenden Hostverkehr: `drop`
- Loopback zulassen
- etablierte Verbindungen zulassen
- ICMP und ICMPv6 zulassen
- nur SSH, HTTP und HTTPS öffnen
- Docker-eigene Tabellen nicht bearbeiten
- veröffentlichte Docker-Ports gesondert betrachten
- keine Datenbankports veröffentlichen

Portfreigaben regelmäßig prüfen:

```bash
sudo ss -lntup
docker ps --format 'table {{.Names}}\t{{.Ports}}'
```

## 3. Docker-Rechte

Benutzer der Gruppe `docker` können Container mit weitreichendem Hostzugriff starten und damit praktisch Root-Rechte erlangen.

Prüfen:

```bash
getent group docker
```

Nur notwendige Administratoren aufnehmen.

## 4. Docker-Socket

Der Docker-Socket ist hochprivilegiert.

Im Core-Stack:

- nur Traefik erhält Zugriff,
- der Mount ist read-only,
- kein Anwendungscontainer erhält den Socket.

Prüfen:

```bash
docker inspect core-traefik \
  --format '{{json .Mounts}}'
```

Read-only verhindert nicht jede missbräuchliche Docker-API-Nutzung. Der Socket bleibt sicherheitskritisch.

## 5. Secrets

- Modus `600`
- nicht in Git
- nicht in Logs
- nicht per Chat oder Ticket verteilen
- verschlüsselt sichern
- nicht ohne Migrationsplan rotieren
- keine Wiederverwendung zwischen unabhängigen Diensten
- keine Secret-Inhalte mit `docker compose config` ausgeben, sofern sie dort als Werte eingebettet wären

Prüfung:

```bash
find <PROJEKT_ROOT>/Compose \
  -path '*/secrets/*' \
  -type f \
  -exec stat -c '%A %n' {} \;
```

## 6. `.env`

`.env` enthält zwar möglichst keine Passwörter, kann aber Domainnamen, E-Mail-Adressen, Volume-Namen und EAB-Werte enthalten.

```bash
chmod 600 .env
git check-ignore -v .env
```

## 7. Updates

- Betriebssystem-Sicherheitsupdates regelmäßig installieren
- Docker und Compose kontrolliert aktualisieren
- Image-Release-Notes lesen
- keine automatischen ungetesteten Hauptversionswechsel
- Backup vor Datenbank- und Authentik-Updates
- nach Updates Logs und Healthchecks prüfen

## 8. Zeit und DNS

Korrekte Zeit ist für TLS und SSO entscheidend:

```bash
timedatectl status
```

DNS-Manipulation oder falsche Einträge können Zertifikatsausstellung und Login-Weiterleitungen beeinträchtigen.

## 9. Backups

Backups enthalten dieselben sensiblen Daten wie das laufende System.

- verschlüsseln
- Zugriff protokollieren
- getrennten Schlüssel verwenden
- mindestens eine externe Kopie
- Wiederherstellung testen
- alte Backups kontrolliert löschen

## 10. Protokolle

Regelmäßig prüfen:

```bash
sudo journalctl -p warning --since=24h
sudo systemctl --failed
docker compose logs --since=24h
```

Keine Secrets in Diagnoseausgaben veröffentlichen.

## 11. Authentik

- Administratoranzahl klein halten
- MFA für Administratoren aktivieren
- starke zufällige Passwörter
- Gruppe `authentik Admins` regelmäßig kontrollieren
- technische Outpost-Benutzer nicht als normale Benutzer behandeln
- fehlgeschlagene Aufgaben und Loginereignisse prüfen

## 12. Minimale Angriffsfläche

Im Core-Stack:

- kein Traefik-Port 8080 am Host
- PostgreSQL ohne Host-Port
- Authentik ohne Host-Port
- Worker ohne Host-Port
- nur Traefik auf 80 und 443
- `exposedByDefault=false`
- nur ausdrücklich gelabelte Dienste werden veröffentlicht
