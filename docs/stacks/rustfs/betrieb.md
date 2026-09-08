# RustFS-Stack: Betrieb

## Endpunkte und Service-Accounts

Ein vertrauter Container tritt dem Netz `rustfs_clients` bei und verwendet
für die S3-API ausschließlich:

```text
Endpoint: http://rustfs:9000
Region: auto
Path style: aktiviert
```

Die öffentliche Adresse `https://s3.<DOMAIN>` ist die geschützte
Browserkonsole, kein allgemeiner Maschinenendpunkt. Browserzugriff und
S3-Service-Accounts sind getrennte Berechtigungen.

Für jede Anwendung gelten eigene Zugangspaare und eine möglichst enge
Bucket-Policy. Root-Credentials werden nicht in Anwendungscontainer gemountet.
Der Langfuse-Account erhält ausschließlich die für seinen Bucket nötigen
Rechte (`ListBucket`, `GetObject`, `PutObject`; `DeleteObject` nur wenn die
Langfuse-Datenaufbewahrung dies später benötigt).

## Konsole und Zugriffsmodell

Die sichtbare Authentik-Kachel führt zu Forward Auth und danach zur nativen
OIDC-Anmeldung in RustFS. Beide sind gewollt. Ein Nutzer ohne
`rustfs-admins` darf weder den Browserweg noch die Konsolenrolle erhalten.

Neue Buckets, Policies und Service-Accounts werden zunächst über die
RustFS-Konsole erstellt. Die spätere zentrale Python-CLI übernimmt diese
speziellen Provisionierungsschritte idempotent; deshalb gibt es bewusst
keinen dauerhaften `rustfs-init`- oder Berechtigungs-Container im Stack.
Docker-Volumes werden bei ihrer Erstellung bereits korrekt verwaltet, während
fachliche Objekte wie Buckets und Accounts Teil der Dienstkonfiguration sind.

## Aktualisierung

Vor einem Update Volume-Backup und OIDC-Test durchführen. Der aktuelle Tag
ist bewusst `1.0.0-beta.11`; kein `latest` verwenden.

```bash
cd <PROJEKT_ROOT>/Compose/rustfs
docker compose pull
docker compose up -d
docker compose ps
```

Danach die internen Healthchecks und den kompletten Browser-/OIDC-Weg gemäß
[Erststart und Prüfung](erststart-und-pruefung.md) wiederholen.
