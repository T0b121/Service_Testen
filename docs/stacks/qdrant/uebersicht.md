# Qdrant-Stack: Übersicht

Qdrant ist die gemeinsame Vektordatenbank für spätere KI-Dienste. Die
browserbasierte Verwaltungsoberfläche ist Bestandteil derselben REST-Adresse
und liegt unter `https://qdrant.<DOMAIN>/dashboard/`. Die Basisadresse `/`
leitet nach erfolgreicher Authentik-Prüfung dorthin weiter.

| Eigenschaft | Wert |
|---|---|
| Image | `qdrant/qdrant:v1.19` (aktuell `1.19.1`) |
| Browserzugriff | `https://qdrant.<DOMAIN>/dashboard` über Traefik und Authentik |
| REST intern | `http://qdrant:6333` im Netzwerk `web` und `qdrant_clients` |
| gRPC intern | `qdrant:6334` im Netzwerk `web` und `qdrant_clients` |
| Persistenz | Docker-Volume `qdrant_storage` |
| Authentik-Gruppe | `qdrant-users` |
| Dienstzugriff | Qdrant-Admin-API-Schlüssel in der lokalen, nicht versionierten `.env` |

Es gibt kein `ports:`-Mapping. REST und gRPC sind daher niemals direkt vom
Host oder Internet erreichbar. Das Dashboard benötigt technisch REST-Aufrufe
im Browser; deshalb ist derselbe HTTPS-Host durch Authentik geschützt. Qdrant
fordert darüber hinaus den API-Schlüssel für alle Verwaltungs- und
Client-Aufrufe.

Weiter mit [Vorbereiten](vorbereiten.md).
