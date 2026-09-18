# RustFS-Stack: Vorbereiten

Voraussetzung ist der funktionierende [Core-Stack](../core/erststart-und-pruefung.md).

## Lokale Konfiguration und Secrets

`Compose/rustfs/.env` bleibt ignoriert und enthält mindestens:

```dotenv
DOMAIN=<DOMAIN>
RUSTFS_VERSION=1.0.0-beta.11
RUSTFS_RC_VERSION=v0.1.33
RUSTFS_OIDC_CLIENT_ID=rustfs-console
```

Unter `Compose/rustfs/secrets/` liegen ausschließlich lokale Dateien:

```text
rustfs_root_access_key
rustfs_root_secret_key
rustfs_oidc_client_secret
langfuse_s3_access_key
langfuse_s3_secret_key
```

`rustfs_root_access_key` und `rustfs_root_secret_key` sind das einzige
Root-Zugangspaar. Sie werden nur bei Administration oder Bootstrap verwendet;
Anwendungen erhalten eigene Service-Accounts. Der OIDC-Client-Secret gehört
zu dem Authentik-Provider `RustFS Console OIDC Provider`. Die beiden
Langfuse-Dateien sind für den späteren Langfuse-Service-Account reserviert,
nicht für den RustFS-Server selbst.

Alle Dateien bleiben lokal und erhalten restriktive Rechte. RustFS läuft als
UID/GID `10001`; die drei von RustFS gelesenen Dateien müssen daher für diesen
Benutzer lesbar sein:

```bash
cd <PROJEKT_ROOT>/Compose/rustfs
chmod 600 .env
chmod 400 secrets/rustfs_root_access_key secrets/rustfs_root_secret_key \
  secrets/rustfs_oidc_client_secret
sudo chown 10001:10001 secrets/rustfs_root_access_key \
  secrets/rustfs_root_secret_key secrets/rustfs_oidc_client_secret
stat -c '%A %u:%g %n' .env secrets/rustfs_root_access_key \
  secrets/rustfs_root_secret_key secrets/rustfs_oidc_client_secret
git check-ignore -v .env secrets/rustfs_root_access_key
```

Ein Secret darf niemals in `.env`, Compose, Git oder Terminal-Ausgaben
kopiert werden. Für zufällige neue Werte kann der Betreiber lokal etwa
`openssl rand -base64 32` ausführen und die Ausgabe direkt in die betreffende
Datei eintragen.

## Netzwerk

`web` existiert bereits durch den Core-Stack. Das zusätzliche interne Netz
für vertrauenswürdige S3-Clients wird einmalig angelegt:

```bash
docker network create --internal rustfs_clients
```

Danach die syntaktische Compose-Prüfung ausführen:

```bash
docker compose config --quiet
```

Weiter mit [Authentik einrichten](authentik-einrichten.md).
