# RustFS-Stack: Übersicht

RustFS stellt den internen, S3-kompatiblen Objektspeicher für Containerdienste
bereit. Die Browserkonsole ist unter `https://s3.<DOMAIN>` verfügbar. Sie ist
zweifach geschützt: Authentik Forward Auth begrenzt den Aufruf der Webseite;
die Konsole meldet den Benutzer zusätzlich über natives Authentik-OIDC an.

| Eigenschaft | Wert |
|---|---|
| Image | `rustfs/rustfs:1.0.0-beta.11` |
| Browserkonsole | `https://s3.<DOMAIN>` über Traefik, Forward Auth und natives OIDC |
| S3 intern | `http://rustfs:9000` ausschließlich im Netz `rustfs_clients` |
| Persistenz | Docker-Volume `rustfs_data` |
| Authentik-Gruppe | `rustfs-admins` |
| Beispiel-Client | Langfuse über einen eigenen S3-Service-Account |

Es existiert kein `ports:`-Mapping. Port `9000` (S3-API) und Port `9001`
(Konsole) sind nur innerhalb der Docker-Netze vorhanden. Externe Rechner
erhalten keinen vorgesehenen Maschinenzugriff auf die S3-API.

Die gewählte Beta-11-Version ist bewusst festgelegt: Die neuere Beta-12-Linie
hatte bei der nativen OIDC-Konsolenanmeldung einen Fehler. Ein Update erfolgt
erst nach einem reproduzierbaren OIDC-Test auf einer neueren Version.

Weiter mit [Vorbereiten](vorbereiten.md).
