# Stack-Vertrag

Der Manager übernimmt gemeinsame Eingaben, Secret-Dateien, Ressourcen,
Authentik-Objekte und Sicherungen. `stack.py` enthält nur Metadaten und besondere
Aktionen. Die Stack-IDs entsprechen den Ordnernamen (`a-z`, Ziffern und Bindestrich).

```python
AUTH_GROUPS = ['example-users', 'example-admins']
TITLE = 'Example'
REQUIRES = ['core']
APPLICATIONS = [{
    'slug': 'example',
    'title': 'Example',
    'routers': ['example'],
    'groups': AUTH_GROUPS,
    'icon': 'https://example.org/icon.png',
}]
```

Jede veröffentlichte Anwendungsroute muss in `APPLICATIONS` erscheinen. Mehrere
Router desselben Hosts teilen eine Beschreibung und dieselben Zugriffsgruppen.
Adressen werden aus den aufgelösten Traefik-Labels übernommen. Der Manager prüft
Forward Auth vor dem Start. Er fügt bei neuen Fremd-Stacks keine Labels stillschweigend
hinzu: Der Stack-Autor muss Middleware und Outpost-Rückweg in Compose definieren.
Die übertragenen Stacks enthalten diese vollständig.

Icons müssen PNG-Dateien über HTTPS sein, maximal 2 MiB. Sie werden zwischengespeichert,
in Authentik hochgeladen und über ihren Inhalt wiederverwendet. Bei Fehlern bleibt
das Standardicon; der Fehler steht unter ausstehenden Aktionen.

## Eingabevorlagen

```dotenv
FIXED=literal
DOMAIN=<global.DOMAIN>
NAME=<NAME=Mein Dienst>
DATABASE_PASSWORD=!<DB_PW | generate="openssl rand -hex 32">
DATABASE_FILE=-<DB_PW | targets=database_password>
APP_FILE=-<APP_KEY | targets=app_key;worker_key | generate="openssl rand -hex 32">
SHARED=!<other-stack.SHARED_KEY>
```

Identisch benannte Referenzen sind standardmäßig stacklokal, z. B. `example.DB_PW`.
`global.` und explizite Stack-Präfixe teilen Werte. Eine einzige vertrauliche Verwendung
macht die gesamte Eingabe vertraulich. Widersprüchliche Defaults oder vorhandene Werte
werden vor einer Änderung gemeldet. `targets=` nennt Compose-Secrets, deren `file:`
innerhalb von `secrets/` liegt. Secret-Vorlagenzeilen erscheinen nicht in der `.env`.
Der Manager führt niemals Shellcode aus Vorlagen oder Eingabewerten aus.

Jeder Dienst mit Datei-Secrets erhält `group_add: ['60001']`. Images mit ausschließlicher
ENV-Unterstützung verwenden `!<…>`. Images mit eigenen Dateisecret-Konventionen werden
in ihrer Compose-Datei entsprechend konfiguriert; generische ENV-zu-Secret-Konvertierung
gibt es nicht.

## SSO und Hooks

```python
SSO = {
    'type': 'oidc', 'slug': 'example', 'application': 'example',
    'client_id_env': 'OIDC_CLIENT_ID',
    'secret': 'oidc_client_secret',
    'callback': '/oauth/callback',
}
```

`secret` ist der Name einer Datei unter `secrets/` oder einer tatsächlichen ENV-Variable.
`client_id_env=None` verwendet den SSO-Slug. OIDC-Subjects sind stabile Authentik-
Benutzer-IDs. SAML wird beim Part-DB-Stack vorgeführt.

Optionale Funktionen:

```python
def before_start(context):
    pass  # Eigene, wiederholbare Vorbereitung nach Ressourcen- und SSO-Anlage.

def after_start(context):
    pass  # Eigene Einrichtung nach erfolgreicher Compose-Bereitschaftsprüfung.

def sync_user(context, action, user):
    pass  # action: create, update, permissions, delete.
```

`context` enthält `stacks`, `docker`, `auth`, `state` und `root`. Bei Fehlern
`ManagerError` auslösen. Hooks dürfen keine allgemeinen ENV- oder Passwortdialoge
implementieren. Sie werden bei erneuter Einrichtung wieder ausgeführt und müssen
idempotent sein. `START_TIMEOUT` überschreibt die Bereitschaftszeit in Sekunden.

Benutzeränderungen werden zuerst in Authentik durchgeführt. Vor einer Löschung wird
der Zugang gesperrt. Die Adapter für GitLab, Nextcloud und Paperless deaktivieren
vorhandene lokale Konten beim Entzug des Zugangs; Anwendungsdaten werden nicht gelöscht.
Andere Anwendungen zeigen die noch separat zu behandelnden lokalen Konten/Sitzungen
im Status. SSO-Claims aktualisieren sich entsprechend der jeweiligen Anwendung beim
Login. Eine sofortige Invalidierung aller Anwendungs-Sitzungen und API-Tokens ist
keine allgemeine Eigenschaft von SSO.

## Zustand und Wiederholung

`compose/_state/state.json` speichert Auswahl, abgeschlossene Schritte, Objekt-IDs,
ausstehende Aktionen und Backup-Aufträge. Passwortwerte liegen dort nicht. Eine
Dateisperre verhindert gleichzeitige CLI-/Backup-Änderungen. ENV und Secrets sind
maßgeblich; fehlende Werte werden ergänzt, vorhandene nicht neu erzeugt.

Teilweise fehlgeschlagene Initialisierung bleibt als ausstehend markiert. Ein Import
mehrerer Mounts ist keine Dateisystemtransaktion über mehrere Datenträger: bei einem
späten Fehler nennt der Manager die bereits ersetzten Ziele. Vorhandene Daten des
aktuell bearbeiteten Verzeichnisses werden während des Austauschs lokal vorgehalten.

Nach einem Fehler während der Wiederherstellung bleiben betroffene Container
gestoppt. Die genannten Importziele prüfen, bevor Dienste wieder gestartet werden.
