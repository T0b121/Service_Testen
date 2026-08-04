# Jellyfin-Stack: Betrieb

## Lokale Jellyfin-Benutzer

Authentik steuert, wer die öffentliche Seite erreichen darf. Jellyfin steuert
anschließend mit lokalen Konten, wer welche Bibliotheken sieht und ob
Transcoding erlaubt ist. Neue Benutzer daher in beiden Systemen gezielt
anlegen; nach Entzug einer Authentik-Gruppenmitgliedschaft endet der äußere
Zugang beim nächsten Login.

## Medienbibliothek

`/media` bleibt für Jellyfin schreibgeschützt. Medien werden später über
Nextcloud in das Volume `jellyfin_media` hochgeladen und danach über
**Dashboard → Bibliotheken → Alle Bibliotheken scannen** eingelesen.

Jellyfin darf keine Löschrechte für die Medienbibliothek erhalten. Metadaten,
Benutzerkonten und Einstellungen speichert Jellyfin bereits in
`jellyfin_config`.

## CPU-Transcoding

Ohne `renderD*`-Gerät verwendet Jellyfin die CPU. Unter
**Dashboard → Wiedergabe → Transcoding** keine Hardwarebeschleunigung
aktivieren. Bei hoher CPU-Last zuerst direkte Wiedergabe im Browser bevorzugen
oder Bitrate und Auflösung reduzieren.

## Update

```bash
cd <PROJEKT_ROOT>/Compose/jellyfin
docker compose config --quiet
docker compose pull
docker compose up -d
docker compose ps
docker compose logs --tail=100 jellyfin
```

Vor Updates [Backup](backup-und-wiederherstellung.md) erstellen. Der Tag
`10.11` übernimmt nur Bugfixes dieser Release-Linie. Haupt- oder
Nebenversionen werden erst nach Release Notes und getestetem Backup bewusst in
`.env` geändert.

## Regelmäßige Kontrollen

```bash
cd <PROJEKT_ROOT>/Compose/jellyfin
docker compose ps
docker compose logs --since=24h jellyfin
docker compose images
```
