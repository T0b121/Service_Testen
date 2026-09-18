#!/usr/bin/env bash
# Setzt die GitLab-Application-Settings, die nicht verlaesslich ueber
# GITLAB_OMNIBUS_CONFIG verwaltet werden. Sicher nach einem Restore erneut
# ausfuehren. Der API-Token wird weder ausgegeben noch gespeichert.
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
stack_dir="$(cd -- "${script_dir}/.." && pwd)"
token_file="${stack_dir}/secrets/gitlab_auth_sync_api_token"
remote_token_file="/tmp/gitlab-security-settings-token-$$"

if [[ ! -r "${token_file}" ]]; then
  echo "Fehlt oder nicht lesbar: ${token_file}" >&2
  exit 1
fi

cleanup() {
  docker exec gitlab rm -f "${remote_token_file}" >/dev/null 2>&1 || true
}
trap cleanup EXIT

docker cp "${token_file}" "gitlab:${remote_token_file}"

docker exec -i gitlab sh -ec '
  token=$(cat "$1")
  curl --fail --silent --show-error --request PUT \
    --header "PRIVATE-TOKEN: ${token}" \
    --data-urlencode "signup_enabled=false" \
    --data-urlencode "vscode_extension_marketplace_single_origin_fallback_enabled=false" \
    http://127.0.0.1/api/v4/application/settings \
  | ruby -rjson -e '\''
      settings = JSON.parse(STDIN.read)
      signup = settings.fetch("signup_enabled")
      fallback = settings.fetch("vscode_extension_marketplace_single_origin_fallback_enabled")
      abort "GitLab hat die Einstellung fuer Registrierungen nicht uebernommen" unless signup == false
      abort "GitLab hat die Web-IDE-Fallback-Einstellung nicht uebernommen" unless fallback == false
      puts "GitLab-Sicherheitseinstellungen gesetzt: Registrierung aus, Web-IDE-Fallback aus."
    '\''
' sh "${remote_token_file}"
