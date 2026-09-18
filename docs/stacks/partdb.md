# Part-DB

[Alle Dienste](../dienste.md) · [Schnellstart](../../SCHNELLSTART.md)

## Was macht der Dienst?

Part-DB verwaltet elektronische Bauteile und deren Lagerbestand.
Bauteile können mit Lagerorten, Kategorien, Bezugsquellen und Projekten verknüpft werden.
Der Stack nutzt MariaDB und separate Volumes für hochgeladene Dateien.
Authentik stellt hier SAML statt OIDC bereit.
Die Zuordnung zu Part-DB-Gruppen wird während der Einrichtung aus der Anwendung gelesen.

## Einordnung in diesem Repository

| Punkt | Konfiguration |
|---|---|
| Stack-ID | `partdb` |
| Browseradresse | `https://partdb.<DOMAIN>` |
| Direkte Abhängigkeiten | [core](core.md) |
| Anmeldung | Forward Auth und SAML |
| Deklarierte Dienstgruppen | `partdb-admin`, `partdb-editor`, `partdb-readonly` |

`<DOMAIN>` steht für die bei der Einrichtung gewählte Basisdomain.
Abhängigkeiten werden vom Manager ergänzt; weitere indirekte Stacks können dazukommen.
Eine Dienstgruppe regelt den äußeren Zugang, nicht automatisch jede Berechtigung innerhalb der Anwendung.

## Bestandteile

| Compose-Service | Container-Image |
|---|---|
| `partdb` | `jbtronics/part-db1:${PARTDB_VERSION}` |
| `mariadb` | `mariadb:${MARIADB_VERSION}` |

Image-Variablen werden aus der Stack-Konfiguration aufgelöst.
Die Tabelle beschreibt den Repository-Stand, keine Liste bereits gestarteter Container.

## Einrichten und starten

Den [Schnellstart](../../SCHNELLSTART.md) einmal für den Host durchführen.
Danach im Manager **Ersteinrichtung** beziehungsweise **Stack-Auswahl ändern** öffnen:

```bash
sudo .venv/bin/python compose/manage.py
```

`partdb` auswählen und die ermittelten Abhängigkeiten kontrollieren.
Vorhandene Werte werden wiederverwendet; neue Secrets gehören nicht in Git.
Erst nach erfolgreicher Einrichtung mit der Nutzung beginnen.

## Erste Nutzung

1. Über `partdb.<DOMAIN>` anmelden und die zugewiesene Rolle prüfen.
2. Einen kleinen Lagerort und eine passende Kategorie anlegen.
3. Ein Testbauteil mit Bezeichnung und Bestand erfassen.
4. Das Bauteil einem einfachen Projekt zuordnen und die Anzeige kontrollieren.
5. Mit einem zweiten Benutzer die reine Lese- beziehungsweise Bearbeitungsrolle testen.

## Wichtige Einstellungen

| Einstellung | Bedeutung |
|---|---|
| `PARTDB_VERSION` | Version der Anwendung. |
| `PARTDB_INSTANCE_NAME` | Anzeigename der Instanz. |
| `PARTDB_DEFAULT_LANG` | Standardsprache; Vorlage `de`. |
| `PARTDB_BASE_CURRENCY` | Basiswährung; Vorlage `EUR`. |
| `PARTDB_SAML_ROLE_MAPPING` | Wird durch die Einrichtung anhand tatsächlicher Gruppen-IDs gesetzt. |

Die vollständigen Eingaben stehen in [`.env.example`](../../compose/partdb/.env.example).
Normale Werte im Manager über **Konfiguration bearbeiten** ändern.
Passwortwechsel sind keine bloßen Textänderungen: Datei und laufender Dienst müssen zusammenpassen.

## Besonderheiten dieser Konfiguration

- Die Dienstgruppen heißen `partdb-admin`, `partdb-editor` und `partdb-readonly`.
- Der Hook ermittelt echte IDs der Gruppen `admins`, `users` und `readonly`; er rät keine Zahlenwerte.
- Unbekannte Rollen werden in der Zuordnung mit `* = -1` behandelt.
- Anonyme Berechtigungen werden während der Einrichtung ausdrücklich eingeschränkt.
- SAML-Zertifikat und privater Schlüssel müssen zusammengehören; der Vorbereitungshook vergleicht ihre öffentlichen Schlüssel.
- Für mehrzeilige Schlüssel und Zertifikate kann der Manager `@file:/absoluter/pfad` verwenden.
- Datenbankmigrationen bleiben beim Anwendungseinstieg mit `DB_AUTOMIGRATE`.
- Öffentliche API- oder KiCad-Integrationen müssen zusätzlich Forward Auth bewältigen.

## Daten und Sicherung

| Volume-Schlüssel | Tatsächlicher Volume-Name |
|---|---|
| `partdb_uploads` | `managed_partdb_uploads` |
| `partdb_public_media` | `managed_partdb_public_media` |
| `mariadb_data` | `managed_partdb_mariadb_data` |

- MariaDB-Daten und beide Dateiablagen gemeinsam berücksichtigen.
- SAML-Schlüsselmaterial und Anwendungsschlüssel für eine Wiederherstellung sichern.
- Ein Datenbankbackup allein bewahrt keine hochgeladenen Anhänge.

Im Manager **Backups / Import / Export** öffnen und Stack, Service und Mounts auswählen.
Alle benötigten Services berücksichtigen; eine einzelne Service-Auswahl ist kein vollständiges Stack-Backup.
Der Manager hält betroffene Schreiber für Mount-Sicherungen an.
Konfiguration kann zusätzlich mit `age` verschlüsselt gesichert werden.
Vor einer Wiederherstellung Ziel-Mounts und vorhandene Daten prüfen.

## Wenn etwas nicht funktioniert

| Beobachtung | Zuerst prüfen |
|---|---|
| Zertifikatprüfung schlägt fehl | Das zusammen erzeugte Zertifikat-Schlüssel-Paar verwenden. |
| Falsche Rolle nach Anmeldung | SAML-Claims und die vom Hook gespeicherte Gruppenzuordnung prüfen. |
| Migration scheitert | MariaDB-Zugriff und Anwendungsversion kontrollieren. |
| Dateianhang fehlt nach Restore | Neben der Datenbank auch Uploads und Medien wiederherstellen. |

Für den Containerstatus und begrenzte Logs im Repository:

```bash
docker compose --project-directory compose/partdb --env-file compose/partdb/.env -p partdb -f compose/partdb/compose.yml ps
docker compose --project-directory compose/partdb --env-file compose/partdb/.env -p partdb -f compose/partdb/compose.yml logs --tail=80
```

Fehlt die `.env`, zuerst die Einrichtung abschließen.
Vor dem Weitergeben von Logs mögliche Zugangsdaten und persönliche Daten entfernen.

## Grenzen und weiterführende Dateien

Diese Seite beschreibt die vorhandene Konfiguration und ersetzt keinen Live-Test.
Ein erfolgreicher Compose-Check beweist weder SSO noch die vollständige Wiederherstellung.

- [Compose-Konfiguration](../../compose/partdb/compose.yml)
- [Stack-Metadaten und Hooks](../../compose/partdb/stack.py)
- [Gemeinsame Manager-Funktionen](../manager.md)
- [Ausstehende Betriebsprüfungen](../validierung.md)
