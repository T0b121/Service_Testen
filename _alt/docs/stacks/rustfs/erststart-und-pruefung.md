# RustFS-Stack: Erststart und Prüfung

## Start

```bash
cd <PROJEKT_ROOT>/Compose/rustfs
docker compose pull
docker compose up -d
docker compose ps
```

`rustfs` muss nach der Startphase den Status `healthy` zeigen. Es dürfen nur
die internen Ports `9000/tcp` und `9001/tcp`, niemals Host-Port-Bindungen,
erscheinen.

## Interne Prüfung

```bash
docker exec rustfs curl -fsS http://127.0.0.1:9000/health
docker exec rustfs curl -fsS http://127.0.0.1:9001/rustfs/console/health
```

Beide Aufrufe müssen erfolgreich sein. Das zeigt nur die Erreichbarkeit; es
ersetzt keinen Berechtigungstest mit einem Service-Account.

## Browserweg und SSO

Ohne Authentik-Sitzung muss die öffentliche Root-Adresse zur Anmeldung
umleiten. Der Outpost-Ping liefert unabhängig davon `204`:

```bash
curl -I https://s3.<DOMAIN>/
curl -I https://s3.<DOMAIN>/outpost.goauthentik.io/ping
```

Danach in einem privaten Browserfenster `https://s3.<DOMAIN>/` öffnen:

1. Authentik Forward Auth mit einem Mitglied von `rustfs-admins` abschließen.
2. Die RustFS-Konsole wird geladen.
3. Dort **Authentik** als OIDC-Anmeldung wählen.
4. Nach der Rückleitung muss die Konsole ohne Root-Schlüssel zugänglich sein.

Der testweise angelegte Bucket `langfuse` ist für den folgenden Langfuse-Stack
vorgesehen. Sein Service-Account wird vor dem produktiven Langfuse-Start mit
List-, Get- und Put-Rechten auf genau diesen Bucket geprüft.

Weiter mit [Betrieb](betrieb.md).
