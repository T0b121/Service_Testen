#!/usr/bin/env bash
# Erzeugt nur fehlende lokale Secrets. Bestehende Werte werden nie ersetzt.
set -euo pipefail

stack_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
secrets_dir="${stack_dir}/secrets"
mkdir -p "${secrets_dir}"
chmod 700 "${secrets_dir}"

create_secret() {
  local name="$1"
  local bytes="$2"
  local target="${secrets_dir}/${name}"
  if [[ -e "${target}" ]]; then
    echo "Bestehendes Secret bleibt unverändert: ${name}"
    return
  fi
  umask 077
  openssl rand -base64 "${bytes}" | tr -d '\n' >"${target}"
  chmod 600 "${target}"
  echo "Secret erzeugt: ${name}"
}

create_secret postgresql_password 36
create_secret paperless_secret_key 64
create_secret paperless_admin_password 36
create_secret paperless_oidc_client_secret 48

# Die OIDC-Konfiguration wird nach dem Anlegen des Authentik-Providers gesetzt.
if [[ ! -e "${secrets_dir}/paperless_socialaccount_providers" ]]; then
  printf '{}' >"${secrets_dir}/paperless_socialaccount_providers"
  chmod 600 "${secrets_dir}/paperless_socialaccount_providers"
  echo "OIDC-Platzhalter erzeugt."
fi
