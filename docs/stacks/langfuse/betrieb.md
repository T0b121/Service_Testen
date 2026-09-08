# Langfuse-Stack: Betrieb

## LiteLLM-Tracing

LiteLLM gehört dem internen Netz `langfuse_clients` an und verwendet:

```text
LANGFUSE_OTEL_HOST=http://langfuse:3000
LANGFUSE_PUBLIC_KEY=<LANGFUSE_PROJECT_PUBLIC_KEY>
LANGFUSE_SECRET_KEY=<LANGFUSE_PROJECT_SECRET_KEY>
Callback: langfuse_otel
```

Die zwei Projekt-Schlüssel werden in `Compose/litellm/.env` als eigene lokale
Variablen `LANGFUSE_PUBLIC_KEY` und `LANGFUSE_SECRET_KEY` hinterlegt. Sie sind
die Werte des Projekts `litellm` aus `Compose/langfuse/.env`; sie werden nicht
in Compose-Dateien und nicht in die LiteLLM-Konfiguration geschrieben. Nach
dem Eintrag LiteLLM neu erstellen:

```bash
cd <PROJEKT_ROOT>/Compose/litellm
docker compose up -d --force-recreate litellm
```

Ein erfolgreicher Modellaufruf über LiteLLM erscheint danach in Langfuse im
Projekt **LiteLLM**. Langfuse selbst braucht für die interne OTel-Aufnahme
keinen öffentlich erreichbaren API-Port.

## S3-Medien

Langfuse speichert Events und Medien mit einem eigenen S3-Service-Account im
RustFS-Bucket `langfuse`. Endpoint und Path-Style sind intern festgelegt:

```text
http://rustfs:9000
Region: auto
Path style: true
```

Der RustFS-Root-Account gehört weder in Langfuse noch in LiteLLM. Der
Service-Account darf nur den Bucket `langfuse` verwenden.

## Aktualisierung

Vor einem Versionswechsel die Volumes sichern und danach sowohl Healthchecks
als auch den SSO-Login und einen LiteLLM-Trace wiederholen:

```bash
cd <PROJEKT_ROOT>/Compose/langfuse
docker compose pull
docker compose up -d
docker compose ps
```
