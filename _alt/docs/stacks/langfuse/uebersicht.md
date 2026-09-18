# Langfuse-Stack: Übersicht

Langfuse speichert und bewertet LLM-Traces. Die Oberfläche ist unter
`https://langfuse.<DOMAIN>` verfügbar. LiteLLM sendet Telemetrie ausschließlich
über das interne Docker-Netz `langfuse_clients` an `http://langfuse:3000`.

| Eigenschaft | Wert |
|---|---|
| Images | Langfuse und Worker `4.30`, PostgreSQL `18`, ClickHouse `26.4`, Valkey `8-alpine` |
| Browseroberfläche | `https://langfuse.<DOMAIN>` über Traefik, Forward Auth und natives OIDC |
| Interne Trace-API | `http://langfuse:3000` im Netz `langfuse_clients` |
| S3-Speicher | RustFS-Bucket `langfuse` im Netz `rustfs_clients` |
| Persistenz | vier Docker-Volumes für PostgreSQL, ClickHouse und Valkey |
| Authentik-Gruppe | `langfuse-users`; `langfuse-admins` ist für spätere administrative Rollen reserviert |

Es gibt keine Host-Port-Bindungen. PostgreSQL, ClickHouse und Valkey sind nur
im internen Stack-Netz erreichbar. RustFS-Zugang und die Langfuse-UI sind
getrennt abgesichert.

Weiter mit [Vorbereiten](vorbereiten.md).
