#!/bin/sh

set -eu

read_secret()
{
    secret_file="$1"
    secret_name="$2"

    if [ ! -r "$secret_file" ]; then
        echo "Fehler: Secret '$secret_name' ist nicht lesbar: $secret_file" >&2
        exit 1
    fi

    secret_value="$(cat "$secret_file")"

    if [ -z "$secret_value" ]; then
        echo "Fehler: Secret '$secret_name' ist leer." >&2
        exit 1
    fi

    printf '%s' "$secret_value"
}

# Erforderliche Konfigurationswerte prüfen.
: "${DOMAIN:?DOMAIN ist nicht gesetzt}"

: "${PARTDB_DEFAULT_LANG:?PARTDB_DEFAULT_LANG ist nicht gesetzt}"
: "${PARTDB_DEFAULT_TIMEZONE:?PARTDB_DEFAULT_TIMEZONE ist nicht gesetzt}"
: "${PARTDB_BASE_CURRENCY:?PARTDB_BASE_CURRENCY ist nicht gesetzt}"
: "${PARTDB_INSTANCE_NAME:?PARTDB_INSTANCE_NAME ist nicht gesetzt}"
: "${PARTDB_SAML_ROLE_MAPPING:?PARTDB_SAML_ROLE_MAPPING ist nicht gesetzt}"

: "${MARIADB_USER:?MARIADB_USER ist nicht gesetzt}"
: "${MARIADB_DATABASE:?MARIADB_DATABASE ist nicht gesetzt}"

# Nur Zeichen erlauben, die in einem normalen DNS-Domainnamen vorkommen.
case "$DOMAIN" in
    ""|*[!A-Za-z0-9.-]*)
        echo "Fehler: DOMAIN enthält unzulässige Zeichen: $DOMAIN" >&2
        exit 1
        ;;
esac

# Allgemeine Secrets einlesen.
APP_SECRET="$(
    read_secret \
        /run/secrets/partdb_app_secret \
        partdb_app_secret
)"

DATABASE_PASSWORD="$(
    read_secret \
        /run/secrets/mariadb_password \
        mariadb_password
)"

# Installationsspezifische SAML-Daten einlesen.
SAML_IDP_X509_CERT="$(
    read_secret \
        /run/secrets/authentik_saml_idp_certificate \
        authentik_saml_idp_certificate
)"

SAML_SP_X509_CERT="$(
    read_secret \
        /run/secrets/partdb_saml_sp_certificate \
        partdb_saml_sp_certificate
)"

SAML_SP_PRIVATE_KEY="$(
    read_secret \
        /run/secrets/partdb_saml_sp_private_key \
        partdb_saml_sp_private_key
)"

# Punkte der Domain für den regulären Ausdruck maskieren.
DOMAIN_REGEX="$(
    printf '%s' "$DOMAIN" \
        | sed 's/\./\\./g'
)"

# Aus DOMAIN abgeleitete Reverse-Proxy-Konfiguration.
export DEFAULT_URI="https://partdb.${DOMAIN}/"
export TRUSTED_HOSTS="^partdb\\.${DOMAIN_REGEX}$"
export TRUSTED_PROXIES="127.0.0.1,REMOTE_ADDR"

# Allgemeine Part-DB-Einstellungen.
export DEFAULT_LANG="$PARTDB_DEFAULT_LANG"
export DEFAULT_TIMEZONE="$PARTDB_DEFAULT_TIMEZONE"
export BASE_CURRENCY="$PARTDB_BASE_CURRENCY"
export INSTANCE_NAME="$PARTDB_INSTANCE_NAME"

# Datenbankkonfiguration.
export APP_SECRET
export DATABASE_URL="mysql://${MARIADB_USER}:${DATABASE_PASSWORD}@mariadb:3306/${MARIADB_DATABASE}?charset=utf8mb4"

# Native SAML-Anmeldung über Authentik.
export SAML_ENABLED="1"
export SAML_BEHIND_PROXY="1"
export SAML_UPDATE_GROUP_ON_LOGIN="true"
export SAML_ROLE_MAPPING="$PARTDB_SAML_ROLE_MAPPING"

# Authentik als SAML Identity Provider.
export SAML_IDP_ENTITY_ID="https://auth.${DOMAIN}/application/saml/partdb-sso/metadata/"
export SAML_IDP_SINGLE_SIGN_ON_SERVICE="https://auth.${DOMAIN}/application/saml/partdb-sso/"
export SAML_IDP_SINGLE_LOGOUT_SERVICE="https://auth.${DOMAIN}/application/saml/partdb-sso/"
export SAML_IDP_X509_CERT

# Part-DB als SAML Service Provider.
export SAML_SP_ENTITY_ID="https://partdb.${DOMAIN}/sp"
export SAML_SP_X509_CERT
export SAML_SP_PRIVATE_KEY

# Nicht mehr benötigte Hilfsvariablen entfernen.
unset DATABASE_PASSWORD
unset DOMAIN_REGEX

# Konsolenbefehle mit derselben Konfiguration wie Part-DB ausführen.
if [ "${1:-}" = "console" ]; then
    shift
    exec sudo -E -u www-data php bin/console "$@"
fi

# Den originalen Part-DB-EntryPoint aus dem Image starten.
exec /usr/local/bin/partdb-entrypoint.sh "$@"
