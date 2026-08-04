# LiteLLM-Stack: Betrieb und Clients

## Verwaltung und Key-Lebenszyklus

Die Oberfläche `https://litellm.<DOMAIN>/ui` verwendet LiteLLM-OIDC gegen
Authentik. Der Master-Key verbleibt beim Administrator. Für jedes Drittsystem
einen separaten Virtual Key anlegen, Modellfreigaben und Limits setzen und den
Zweck dokumentieren. Der lokale Fallback-Login unter `/fallback/login` ist nur
für Störungen des nativen LiteLLM-OIDC-Logins gedacht. Er liegt weiterhin
hinter Authentik Forward Auth und funktioniert daher nicht als Umgehung bei
einem vollständigen Authentik-Ausfall.

Bei Verlust oder Ablösung eines Systems dessen Virtual Key widerrufen statt
einen gemeinsamen Key weiterzuverwenden.

Für produktive Maschinenclients den Key einem `Service Account` zuordnen und
die Modellfreigabe auf die tatsächlich benötigten Modelle beschränken. Der
Test-Key eines persönlichen Administratorkontos ist kein Ersatz dafür.

## OpenAI-kompatibler Client

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://litellm.<DOMAIN>/v1",
    api_key="<VIRTUAL_KEY>",
)

response = client.chat.completions.create(
    model="qwen3:0.6b",
    messages=[{"role": "user", "content": "Antworte ausschließlich mit OK."}],
)
print(response.choices[0].message.content)
```

Die API erwartet genau einen Header `Authorization: Bearer <VIRTUAL_KEY>`.
Authentik-Tokens oder der LiteLLM-Master-Key gehören nicht auf Client-Systeme.

## Update und Status

```bash
cd <PROJEKT_ROOT>/Compose/litellm
docker compose ps
docker compose logs --tail=200 litellm
docker compose pull
docker compose up -d
```

Vor jedem Update Release Notes prüfen. `LITELLM_MASTER_KEY` und
`LITELLM_SALT_KEY` niemals während eines Updates ersetzen.
