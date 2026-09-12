# Paperless-ngx: Betrieb

Die Oberfläche ist unter `https://paperless.<DOMAIN>` erreichbar. Dokumente
werden über den Browser hochgeladen oder in das Volume `paperless_consume`
gelegt. Unterordner des Consume-Ordners werden als Tags übernommen.

## Automation und API

Andere Dienste greifen ausschließlich über die Paperless-API zu:

```text
http://paperless:8000/api/
```

Für n8n, Flowise oder Open WebUI wird je Integration ein eigener API-Token in
Paperless erzeugt und nur in deren jeweiliger Credential-Verwaltung abgelegt.
Die Dienste erhalten weder Zugriff auf PostgreSQL noch auf die Docker-Volumes
oder RustFS. Dokumentimport erfolgt über `POST /api/documents/post_document/`.

## Betriebskommandos

```bash
cd <PROJEKT_ROOT>/Compose/paperless
docker compose ps
docker compose logs -f paperless
docker compose pull
docker compose up -d
```

Die CPU-Arbeit ist begrenzt auf zwei Worker mit jeweils zwei OCR-Threads. Das
ist für einen einzelnen Nutzer ein guter Durchsatz, ohne den Host dauerhaft zu
belegen. Bei langen Importwarteschlangen können diese Werte bewusst angepasst
werden; ihre Multiplikation darf die verfügbare CPU-Kapazität nicht übersteigen.
