#!/bin/sh
set -eu

# Das offizielle Image kennt nur JWT_SECRET als Umgebungsvariable. Das Secret
# wird deshalb erst im Container aus dem Docker-Secret gelesen und erscheint
# weder in Compose noch in "docker inspect".
export JWT_SECRET="$(cat /run/secrets/onlyoffice_jwt_secret)"
exec /app/ds/run-document-server.sh
