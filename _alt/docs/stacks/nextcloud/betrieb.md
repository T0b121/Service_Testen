# Nextcloud-Stack: Betrieb

## Status und Logs

```bash
cd <PROJEKT_ROOT>/Compose/nextcloud
docker compose ps
docker compose logs --tail=100
docker compose logs --since=15m nextcloud onlyoffice
```

## Starten und stoppen

```bash
docker compose start
docker compose stop
docker compose down
docker compose up -d
```

`docker compose down -v` ist kein normaler Betriebsbefehl: Er löscht
Nextcloud-, Datenbank- und ONLYOFFICE-Daten.

## Nextcloud-Wartung

```bash
docker compose exec -u www-data nextcloud php occ status
docker compose exec -u www-data nextcloud php occ maintenance:repair
docker compose exec -u www-data nextcloud php occ db:add-missing-indices
```

## OIDC-Zugang verwalten

Die Berechtigung für neue Nextcloud-Anmeldungen liegt in Authentik in der
Gruppe `nextcloud-users`. Mitglieder der Authentik-Gruppe
`nextcloud-admins` erhalten über den OIDC-Gruppen-Claim zusätzlich die echte
Nextcloud-Gruppe `admin`. Die App `user_oidc` legt berechtigte Benutzer beim
ersten erfolgreichen OIDC-Login an. Das anfangs benötigte lokale Bootstrap-
Konto wird nach dem OIDC-Test deaktiviert und ist kein regulärer Zugang.

Die Gruppenmitgliedschaft wird beim nächsten OIDC-Login abgeglichen. Für eine
Entziehung von Zugriffs- oder Administratorrechten die Authentik-Gruppen
ändern und den Benutzer anschließend erneut anmelden lassen.

### Lokalen Bootstrap-Admin wiederherstellen

Der lokale Benutzer `admin` ist nach der Ersteinrichtung deaktiviert. Er ist
nur ein Notfallzugang bei einer vollständigen OIDC-Störung und wird über SSH
wieder eingeschaltet. Die vollständige, verifizierte Befehlsfolge einschließlich
der erneuten Deaktivierung steht in der
[Fehlerbehebung](fehlerbehebung.md#oidc-anmeldung-leitet-nicht-zu-authentik-weiter).
Es ist kein lokaler Desktop am Server erforderlich.

Den OIDC-Provider nicht löschen: Das kann den Zugang bereits angelegter
OIDC-Benutzer ungültig machen. Bei einer Änderung der OIDC-Konfiguration
zuerst einen Login im privaten Browserfenster testen. Bei einer vollständigen
OIDC-Störung erfolgt die Wiederherstellung per SSH und `occ`; sie benötigt
keinen grafischen Zugriff auf den Server.

## Aktualisieren

Vorher das [Backup](backup-und-wiederherstellung.md) erstellen und Release
Notes lesen. Dann:

```bash
docker compose config --quiet
docker compose pull
docker compose up -d
docker compose ps
docker compose logs --tail=150
```

Vor einem ONLYOFFICE-Neustart offene Dokumente schließen. ONLYOFFICE schreibt
Änderungen erst beim Schließen der letzten Bearbeitungssitzung zuverlässig an
Nextcloud zurück. Für einen geplanten Neustart:

```bash
docker compose exec onlyoffice documentserver-prepare4shutdown.sh
docker compose up -d --force-recreate onlyoffice
```

Die Tags folgen kontrollierten Release-Linien: Nextcloud 34, PostgreSQL 18
und Redis 8. ONLYOFFICE ist auf die aktuell geprüfte Vollversion gepinnt, weil
der Hersteller keinen verlässlich gepflegten 9.4-Linien-Tag anbietet. Neue
ONLYOFFICE-Releases werden nach Release-Notes- und Backup-Prüfung bewusst in
der lokalen `.env` eingetragen.

## Spätere n8n-Anbindung

n8n wird nicht Teil dieses Stacks. Es erhält später einen eingeschränkten
Nextcloud-Service-Account mit App-Passwort und Zugriff nur auf freigegebene
Ordner über WebDAV/API. Es erhält weder Docker-Volume-Zugriff noch Zugang zum
ONLYOFFICE-Secret.
