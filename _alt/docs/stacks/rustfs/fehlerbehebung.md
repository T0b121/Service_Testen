# RustFS-Stack: Fehlerbehebung

## Konsole zeigt nur Schlüssel- und STS-Anmeldung

Dann liefert RustFS keinen OIDC-Provider. Prüfen:

1. Die Redirect-URI ist exakt
   `https://s3.<DOMAIN>/rustfs/admin/v3/oidc/callback/default`.
2. Der Authentik-OIDC-Provider hat einen Signing Key.
3. `RUSTFS_IDENTITY_OPENID_CONFIG_URL` enthält den korrekten extern
   erreichbaren Authentik-Issuer mit dem Slug `rustfs-console`.
4. RustFS nach einer OIDC-Änderung neu erstellen:

```bash
cd <PROJEKT_ROOT>/Compose/rustfs
docker compose up -d --force-recreate rustfs
docker compose logs --tail=100 rustfs
```

## OIDC-Callback oder Forward Auth führt in eine Schleife

Der Traefik-Router für `/outpost.goauthentik.io/` muss direkt den Embedded
Outpost bedienen und darf nicht selbst die `authentik@docker`-Middleware
erhalten. Der Console-Router für `/rustfs/console` muss auf Port `9001`, alle
übrigen RustFS-Admin-, OIDC- und S3-Pfade auf Port `9000` zeigen.

## Zugriff verweigert, obwohl die Anmeldung gelingt

Mitgliedschaft in `rustfs-admins` prüfen. Beide Authentik-Anwendungen haben
eigene Gruppenbindings; ein fehlendes Binding in nur einer Schicht reicht für
einen Fehler. Zusätzlich kann eine RustFS-Policy den angemeldeten Benutzer
einschränken.

## Container startet nicht wegen Secret-Fehlern

Prüfen, dass die drei RustFS-Secrets existieren und UID/GID `10001:10001`
sowie Modus `0400` tragen:

```bash
cd <PROJEKT_ROOT>/Compose/rustfs
stat -c '%A %u:%g %n' secrets/rustfs_root_access_key \
  secrets/rustfs_root_secret_key secrets/rustfs_oidc_client_secret
docker compose config --quiet
docker compose logs --tail=100 rustfs
```

Nicht auf `chmod 644` ausweichen. Stattdessen Besitzer und Modus gezielt
korrigieren.

## Ein interner Client erreicht RustFS nicht

Der Client muss Mitglied von `rustfs_clients` sein und
`http://rustfs:9000` verwenden. Die öffentliche `https://s3.<DOMAIN>`-Adresse
ist wegen Forward Auth für interne Maschinenkommunikation ungeeignet.
