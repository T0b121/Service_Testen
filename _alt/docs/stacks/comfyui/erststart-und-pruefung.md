# ComfyUI: Erststart und Prüfung

```bash
cd <PROJEKT_ROOT>/Compose/comfyui
cp .env.example .env
chmod 600 .env
docker compose config --quiet
docker compose up -d
./scripts/configure-authentik-access.sh
docker compose ps
```

Danach `https://comfyui.<DOMAIN>` öffnen. Authentik muss vor der ComfyUI-
Oberfläche erscheinen. Ein Mitglied von `comfyui-users` darf die Oberfläche
verwenden; ein Mitglied von `comfyui-admins` erhält derzeit denselben
ComfyUI-Zugriff, da ComfyUI selbst keine separaten Rollen kennt.

Modelle und Custom Nodes nur bewusst aus vertrauenswürdigen Quellen hinzufügen:
Sie werden im ComfyUI-Container ausgeführt und sind deshalb wie installierter
Code zu behandeln.
