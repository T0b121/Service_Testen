# Core-Stack: Authentik verwalten

Dieses Dokument enthält Zusatzinformationen für den laufenden Betrieb. Die Grundkonfiguration des Traefik-Dashboards steht in [authentik-einrichten.md](authentik-einrichten.md).

## 1. Benutzerarten

Navigation:

```text
Directory → Users → New User
```

Der Assistent zeigt drei auswählbare Benutzertypen:

| Typ | Zweck | Typische Verwendung |
|---|---|---|
| `Internal User` | interaktiver menschlicher Benutzer mit Zugriff auf die Authentik-Benutzeroberfläche und – bei entsprechenden Rechten – die Adminoberfläche | Administratoren, interne Benutzer, normale Testbenutzer |
| `External User` | menschlicher Benutzer für B2C-, Gast- oder externe Anwendungszugriffe; kein Zugriff auf Authentiks Application Dashboard und User Settings | Kunden, Gäste oder externe Partner, die direkt zu einer Anwendung weitergeleitet werden |
| `Service Account` | nicht-interaktives Maschinenkonto ohne normales Benutzerpasswort; verwendet App Passwords oder API-Tokens | Skripte, API-Zugriffe, LDAP-Bind, Automatisierung und Integrationen |

Für einen einfachen Test des Traefik-Dashboards wird **`Internal User`** verwendet. Ein `External User` ist dafür ungeeignet, weil externe Benutzer nicht die normale Authentik-Benutzeroberfläche verwenden. Ein `Service Account` repräsentiert keine Person und darf nicht als Browser-Testkonto verwendet werden.

Das automatisch erzeugte Konto `ak-outpost-...` ist ein internes Servicekonto von Authentik. Es wird nicht manuell verändert.

<a id="internen-benutzer-oder-testbenutzer-anlegen"></a>

## 2. Internen Benutzer oder Testbenutzer anlegen

1. Unter `Directory → Users` den gewünschten Benutzerordner auswählen. Für normale Benutzer ist `users` vorgesehen.
2. `New User` anklicken.
3. `Internal User` auswählen.
4. Die Felder ausfüllen.

### Felder

| Feld | Bedeutung | Empfehlung für einen Testbenutzer |
|---|---|---|
| `Anmeldename` / Username | eindeutiger primärer Bezeichner für die Anmeldung | `testuser` oder ein anderer eindeutiger Name |
| `Display Name` | optionaler Anzeigename | `Test User` |
| `Email Address` | optional; für E-Mail-Stages, Recovery und Benachrichtigungen | wegen der aktuell gesperrten SMTP-Verbindung leer lassen oder nur als Kontaktinformation eintragen |
| `Aktiv` | erlaubt die Anmeldung | aktiviert |
| `Pfad` | organisatorischer Benutzerordner | `users` |
| `Attribute` | optionale benutzerdefinierte Daten als JSON oder YAML | unverändert `{}` |

### Pfad

Der Pfad ist ein Pflichtfeld und dient nur der Organisation. Er vergibt keine Rechte und ändert keine Gruppenmitgliedschaft.

Regeln:

- normaler Standard: `users`
- optionale Unterordner: `users/test`, `users/intern` oder `users/extern`
- kein führender Slash: nicht `/users`
- kein abschließender Slash: nicht `users/`
- bei vorher ausgewähltem Benutzerordner wird der Pfad normalerweise automatisch passend vorbelegt

Für den Testbenutzer:

```text
Type: Internal User
Anmeldename: testuser
Display Name: Test User
Email Address: leer oder <TEST_EMAIL>
Aktiv: Ja
Pfad: users
Attribute: {}
```

Nach `Create` muss der Benutzer in der Liste als aktiv und vom Typ `Intern` beziehungsweise `Internal User` erscheinen.

### Passwort setzen

Das Erstellungsformular enthält kein Passwortfeld. Nach der Erstellung:

1. Benutzer öffnen oder den Pfeil neben dem Benutzer ausklappen.
2. `Reset password` beziehungsweise `Passwort zurücksetzen` auswählen.
3. ein starkes Initialpasswort setzen.

Ein zufälliges Passwort:

```bash
openssl rand -base64 24
```

Die Ausgabe direkt in einen Passwortmanager übernehmen. Sie darf nicht in Git, eine Markdown-Datei oder ein Shellskript geschrieben werden.

Für den Zugriffs-Negativtest darf der Testbenutzer **nicht** Mitglied von `authentik Admins` sein. Erwartet beim Aufruf von `https://proxy.<DOMAIN>/dashboard/`: Anmeldung funktioniert, der Zugriff auf das Dashboard wird anschließend verweigert.

<a id="provider-authorization-flows"></a>

## 3. Provider-Authorization-Flows

Beim Erstellen eines Providers stehen in der aktuellen Oberfläche typischerweise diese beiden Authorization Flows zur Auswahl:

| Flow | Verhalten | Geeignet für |
|---|---|---|
| `default-provider-authorization-implicit-consent` | autorisiert ohne zusätzliche Zustimmungsseite; vorhandene Bindings und Policies werden weiterhin ausgewertet | interne, vertrauenswürdige Anwendungen wie das Traefik-Dashboard |
| `default-provider-authorization-explicit-consent` | enthält eine Consent-Stufe und fragt den Benutzer ausdrücklich nach Zustimmung zur Datenfreigabe | Anwendungen, bei denen Benutzer die Freigabe bewusst bestätigen sollen |

Für den Core-Stack wird verwendet:

```text
default-provider-authorization-implicit-consent
```

`implicit consent` bedeutet hier nicht, dass Zugriffskontrollen übersprungen werden. Gruppenbindungen, Benutzerbindungen und Policies entscheiden weiterhin, ob die Anwendung genutzt werden darf.

## 4. Benutzer deaktivieren

Bei temporärem Entzug:

- Benutzer öffnen
- `Active` deaktivieren
- aktive Sitzungen bei Bedarf widerrufen
- Gruppenmitgliedschaften kontrollieren

Deaktivieren ist meist sicherer als sofortiges Löschen, weil Referenzen und Auditdaten erhalten bleiben.

## 5. Benutzer löschen

Vorher prüfen:

- besitzt der Benutzer administrative Rechte?
- ist er Eigentümer oder Teil wichtiger Bindings?
- werden Auditdaten benötigt?
- existiert ein anderer funktionierender Administrator?

Den Standardbenutzer `akadmin` nicht unüberlegt löschen.

## 6. Gruppen anlegen

Navigation:

```text
Directory → Groups
```

Gruppen nach Berechtigungszweck benennen, nicht nach einzelnen Personen.

Beispiele:

```text
cloud-users
stream-admins
service-readonly
```

Benutzer einer Gruppe hinzufügen und Zugriffsbindungen bevorzugt an Gruppen statt an Einzelbenutzer hängen.

## 7. Gruppe `authentik Admins`

Mitglieder dieser Gruppe besitzen weitreichende Authentik-Rechte und können außerdem das geschützte Traefik-Dashboard erreichen.

Regeln:

- Mitglieder regelmäßig kontrollieren.
- nur notwendige Administratoren aufnehmen.
- MFA aktivieren.
- getrennte normale und administrative Konten erwägen.
- ausgeschiedene Benutzer sofort entfernen oder deaktivieren.

## 8. Anwendungsbindungen

Bei einer Anwendung:

- Gruppenbindung bevorzugen
- `Negate` nur bei bewusstem Ausschlussmodell verwenden
- Reihenfolge dokumentieren
- Failure Result prüfen
- Zugangsprüfung mit mehreren Benutzern durchführen

Ohne Bindings können Anwendungen für alle Benutzer zugänglich sein.

<a id="mfa-für-administratoren"></a>

## 9. MFA für Administratoren

Empfohlen:

- Passkey beziehungsweise WebAuthn
- TOTP als zusätzliches Verfahren
- Wiederherstellungsmöglichkeit sicher verwahren
- mindestens zwei unabhängige Verfahren bei kritischen Administratorkonten

Die Registrierung erfolgt über die Benutzereinstellungen beziehungsweise den dafür konfigurierten Enrollment-Flow.

Prüfen:

1. Administrator meldet sich ab.
2. neue Anmeldung durchführen.
3. MFA-Abfrage kontrollieren.
4. Wiederherstellungsverfahren getrennt testen.

Wiederherstellungscodes sind Secrets. Sie werden wie Passwörter behandelt und nicht unverschlüsselt im Repository gespeichert.

## 10. Administratorpasswort ändern

```bash
cd <PROJEKT_ROOT>/Compose/core

docker compose exec \
  authentik-server \
  ak changepassword akadmin
```

Die Eingabe erfolgt interaktiv und erscheint nicht als Klartext im Befehl.

## 11. Recovery Key

Nur verwenden, wenn normale Anmeldung und Passwortwiederherstellung nicht möglich sind.

```bash
docker compose run --rm \
  authentik-server \
  create_recovery_key 10 akadmin
```

Der ausgegebene Link gewährt direkten Zugriff für die angegebene Anzahl Minuten.

Regeln:

- Ausgabe als Secret behandeln.
- nicht in Logs oder Tickets kopieren.
- nur lokal und kurzzeitig verwenden.
- nach erfolgreicher Wiederherstellung Passwort und MFA prüfen.

## 12. E-Mail-Versand: aktueller Stand

Der aktuelle Server darf aufgrund einer übergeordneten Firewall keine E-Mails versenden. Deshalb ist SMTP nicht Teil der Grundinstallation.

Folgen:

- keine Passwortzurücksetzung per E-Mail
- keine E-Mail-Einladungen
- keine E-Mail-Stages
- keine normalen E-Mail-Benachrichtigungen

Administratoren benötigen daher:

- funktionierendes MFA-Wiederherstellungsverfahren
- sicheren Zugriff auf das Adminpasswort
- dokumentierten Recovery-Key-Ablauf

## 13. Optionaler externer SMTP-Relay

Nur später einrichten, wenn die übergeordnete Firewall und das Worker-Netzwerk den Zielserver erreichen dürfen.

Benötigte Werte:

```text
SMTP-Hostname
SMTP-Port
TLS- oder SSL-Modus
Benutzername
Passwort oder App-Passwort
Absenderadresse
```

Das SMTP-Passwort wird normalerweise vom Mailanbieter erzeugt. Ein App-Passwort darf nicht durch ein zufälliges lokales Passwort ersetzt werden.

Falls ein selbst verwalteter Relay ein frei wählbares Passwort verlangt:

```bash
umask 077
openssl rand -base64 32 \
  | tr -d '\n' \
  > secrets/authentik_email_password
```

Alternativ ein vom Anbieter ausgegebenes Passwort ohne Shell-History speichern:

```bash
umask 077
read -rsp 'SMTP-Passwort: ' SMTP_PASSWORD
printf '%s' "$SMTP_PASSWORD" \
  > secrets/authentik_email_password
unset SMTP_PASSWORD
printf '\n'
```

Danach:

```bash
chmod 600 secrets/authentik_email_password
stat -c '%A %n' secrets/authentik_email_password
```

Erwartet:

```text
-rw------- secrets/authentik_email_password
```

<a id="netzwerk-für-e-mail-und-externe-aufgaben"></a>

## 14. Netzwerk für E-Mail und externe Aufgaben

Der Worker hängt aktuell nur im internen Netzwerk `core_auth` und hat keinen allgemeinen Internet-Egress.

Für SMTP oder externe Synchronisierung später:

- separates nicht internes Egress-Netzwerk anlegen,
- nur Worker anschließen, sofern nur er Egress benötigt,
- keine Host-Ports veröffentlichen,
- Zielverkehr zusätzlich über Host- oder Provider-Firewall begrenzen,
- Worker nicht allein deshalb in `web` aufnehmen.

## 15. E-Mail testen

Nach einer späteren SMTP-Konfiguration:

```bash
docker compose exec \
  authentik-worker \
  ak test_email <EMPFAENGER_EMAIL>
```

Ohne freigegebenes Netzwerk oder Firewallregel wird der Test fehlschlagen.

## 16. Hintergrundaufgaben

In der Authentik-Adminoberfläche regelmäßig prüfen:

```text
System → Tasks
```

Achten auf:

- dauerhaft wartende Aufgaben
- fehlgeschlagene E-Mail-Aufgaben
- fehlgeschlagene Synchronisierungen
- wiederholte Retries
- Worker nicht erreichbar

## Offizielle Referenzen

- [Authentik First Steps](https://docs.goauthentik.io/install-config/first-steps/)
- [Authentik: Benutzer verwalten](https://docs.goauthentik.io/users-sources/user/user_basic_operations/)
- [Authentik: Service Accounts](https://docs.goauthentik.io/sys-mgmt/service-accounts/)
- [Authentik: Default Flows](https://docs.goauthentik.io/add-secure-apps/flows-stages/flow/examples/default_flows/)
- [Authentik: Consent Stage](https://docs.goauthentik.io/add-secure-apps/flows-stages/stages/consent/)
- [Authentik Worker](https://docs.goauthentik.io/worker/)
- [Authentik E-Mail](https://docs.goauthentik.io/install-config/email/)
- [Authentik Login Recovery](https://docs.goauthentik.io/troubleshooting/login/)
