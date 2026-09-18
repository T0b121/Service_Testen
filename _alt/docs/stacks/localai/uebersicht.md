# LocalAI: Übersicht

LocalAI stellt eine lokal betriebene, OpenAI-kompatible Modell-API und eine
Weboberfläche bereit. Der Dienst hat in der aktuellen Testphase keine CPU- oder
RAM-Grenze. Beim Start setzt er seine Thread-Anzahl dynamisch auf alle
verfügbaren Host-CPUs. Er lädt **kein** Modell; Modelle werden bewusst erst
über die Oberfläche oder die API hinzugefügt.

Die Anmeldung erfolgt nativ über Authentik-OIDC. Lokale LocalAI-Passwörter sind
deaktiviert. Die Gruppen `localai-users` und `localai-admins` begrenzen den
Authentik-Zugriff; die in `.env` angegebene Administrations-E-Mail erhält die
LocalAI-Administrationsrolle.

Öffentlich erreichbar ist nur `https://localai.<DOMAIN>` über Traefik. Der
Container veröffentlicht keinen Host-Port. Vertrauenswürdige Container können
die API unter `http://localai:8080/v1` erreichen, benötigen dafür aber einen
in LocalAI erzeugten persönlichen oder dienstbezogenen API-Schlüssel.
