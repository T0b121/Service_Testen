# Jellyfin-Stack: Übersicht

Jellyfin stellt eine private Medienbibliothek unter
`https://jellyfin.<DOMAIN>` bereit. Der Browserzugriff wird vor der
Auslieferung über Authentik Forward Auth geschützt; anschließend meldet sich
der Benutzer mit einem lokalen Jellyfin-Konto an.

| Bestandteil | Aufgabe |
|---|---|
| Jellyfin | Medienbibliothek, Streaming und Transcoding im Browser |
| `jellyfin_config` | Konfiguration, Benutzerkonten, Datenbank und Metadaten |
| `jellyfin_cache` | Transcoding- und Laufzeitcache |
| `jellyfin_media` | gemeinsame Medienbibliothek, für Jellyfin schreibgeschützt |

Jellyfin verwendet ausschließlich das externe Docker-Netzwerk `web`; Traefik
ist der einzige veröffentlichte Dienst. Weder TCP 8096 noch DLNA-Ports werden
am Host geöffnet. Dadurch ist dieser Stack bewusst für Browsernutzung und
nicht für Discovery in nativen Jellyfin-Apps ausgelegt.

`jellyfin_media` ist ein separates Docker-Volume. Jellyfin bindet es unter
`/media` mit `:ro` ein und kann Dateien daher weder hochladen, ändern noch
löschen. Ein späterer Nextcloud-Stack wird dasselbe Volume als lokalen externen
Speicher schreibbar einhängen. Nextclouds eigene Datenablage wird dabei nie
direkt von Jellyfin gelesen.

Hardware-Transcoding ist zunächst deaktiviert: Auf dem Server existiert kein
`/dev/dri/renderD*`-Gerät. Jellyfin verwendet bei nötigem Transcoding die CPU.

Voraussetzung ist ein gesunder [Core-Stack](../core/erststart-und-pruefung.md).

Weiter mit [Vorbereiten](vorbereiten.md).
