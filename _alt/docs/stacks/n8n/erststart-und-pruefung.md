# n8n-Stack: Erststart und Prüfung

## Start

```bash
cd <PROJEKT_ROOT>/Compose/n8n
docker compose pull
docker compose up -d
docker compose ps
```

`n8n-postgresql`, `n8n` und `n8n-runners` müssen `healthy` sein. Es darf keine
Host-Port-Bindung geben.

## Browser, Anmeldung und Runners

`https://n8n.<DOMAIN>` ohne Authentik-Sitzung aufrufen. Es muss die
Authentik-Anmeldung erscheinen; danach folgt die lokale n8n-Anmeldung oder
die einmalige Anlage des lokalen Besitzeraccounts.

Die Code-Runners werden ohne die optionale n8n-AI-Sandbox betrieben. Diese
Sandbox würde einen privilegierten Docker-in-Docker-Dienst benötigen und ist
absichtlich deaktiviert. JavaScript- und Python-Code-Nodes laufen stattdessen
im separaten `n8n-runners`-Container.

Ein kurzer Test je Code-Node:

```javascript
return [{ json: { runner: "JavaScript funktioniert", ergebnis: 21 * 2 } }];
```

```python
return [{"json": {"runner": "Python funktioniert", "ergebnis": 21 * 2}}]
```

Der Kuma-Monitor **n8n** prüft `http://n8n:5678/healthz`.

Weiter mit [Betrieb](betrieb.md).
