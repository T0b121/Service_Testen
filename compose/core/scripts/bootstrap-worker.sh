#!/bin/sh
set -eu
if [ -f /manager-secrets/manager_bootstrap_password ]; then
  export AUTHENTIK_BOOTSTRAP_PASSWORD="$(cat /manager-secrets/manager_bootstrap_password)"
  export AUTHENTIK_BOOTSTRAP_TOKEN="$(cat /manager-secrets/manager_api_token)"
fi
exec /lifecycle/ak worker
