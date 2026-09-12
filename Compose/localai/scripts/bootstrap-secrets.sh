#!/usr/bin/env bash
# Erzeugt nur fehlende lokale Secrets. Bestehende Werte werden nie ersetzt.
set -euo pipefail

stack_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
secrets_dir="${stack_dir}/secrets"
mkdir -p "${secrets_dir}"
chmod 700 "${secrets_dir}"

target="${secrets_dir}/localai_oidc_client_secret"
if [[ -e "${target}" ]]; then
  echo "Bestehendes Secret bleibt unverändert: localai_oidc_client_secret"
  exit 0
fi

umask 077
openssl rand -base64 48 | tr -d '\n' >"${target}"
chmod 600 "${target}"
echo "Secret erzeugt: localai_oidc_client_secret"
