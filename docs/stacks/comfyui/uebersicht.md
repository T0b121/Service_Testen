# ComfyUI: Übersicht

ComfyUI ist eine grafische Oberfläche für node-basierte Bild- und Medien-Workflows.
Der Server besitzt keine NVIDIA-GPU, daher läuft ComfyUI ausdrücklich mit
`--cpu`. Die Bedienoberfläche funktioniert normal, Bildgenerierung ist jedoch
deutlich langsamer als mit einer GPU.

Beim Start werden keine Modelle heruntergeladen. Das persistente Volume
`comfyui_data` enthält Modelle, Workflows, Custom Nodes, Eingaben und Ausgaben.
Der Dienst hat in der aktuellen Testphase keine CPU- oder RAM-Grenzen und
veröffentlicht keinen Host-Port. Nur Traefik stellt `https://comfyui.<DOMAIN>`
bereit.

Authentik Forward Auth schützt die öffentliche Oberfläche. Die Gruppen
`comfyui-users` und `comfyui-admins` erhalten Zugriff und werden bei der
Einrichtung aus den entsprechenden GitLab-Gruppen initial befüllt.
