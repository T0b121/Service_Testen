#!/usr/bin/env bash
set -euo pipefail

stack_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${stack_dir}"

set -a
# shellcheck disable=SC1091
. ./.env
set +a

client_secret=$(<secrets/localai_oidc_client_secret)

docker exec \
  -e LOCALAI_CLIENT_SECRET="${client_secret}" \
  -e LOCALAI_DOMAIN="${DOMAIN}" \
  core-authentik-server ak shell -c '
import os
from django.core.cache import cache
from authentik.core.api.applications import user_app_cache_key
from authentik.core.models import Application, Group
from authentik.providers.oauth2.models import OAuth2Provider

users, _ = Group.objects.get_or_create(name="localai-users")
admins, _ = Group.objects.get_or_create(name="localai-admins")
gitlab_users = Group.objects.get(name="gitlab-users")
gitlab_admins = Group.objects.get(name="gitlab-admins")
users.users.add(*gitlab_users.users.all())
admins.users.add(*gitlab_admins.users.all())

template = Application.objects.get(slug="gitlab").provider.oauth2provider
defaults = {
    "client_id": "localai",
    "client_secret": os.environ["LOCALAI_CLIENT_SECRET"],
    "client_type": "confidential",
    "authentication_flow": template.authentication_flow,
    "authorization_flow": template.authorization_flow,
    "signing_key": template.signing_key,
    "grant_types": ["authorization_code"],
    "access_code_validity": template.access_code_validity,
    "access_token_validity": template.access_token_validity,
    "refresh_token_validity": template.refresh_token_validity,
    "include_claims_in_id_token": True,
    "sub_mode": template.sub_mode,
    "issuer_mode": template.issuer_mode,
    "logout_method": template.logout_method,
    "_redirect_uris": [{
        "url": "https://localai.{}/api/auth/oidc/callback".format(os.environ["LOCALAI_DOMAIN"]),
        "matching_mode": "strict",
        "redirect_uri_type": "authorization",
    }],
}
provider, created = OAuth2Provider.objects.get_or_create(
    name="LocalAI OIDC Provider", defaults=defaults
)
if not created:
    for field, value in defaults.items():
        setattr(provider, field, value)
    provider.save()
provider.property_mappings.set(template.property_mappings.all())

app, _ = Application.objects.get_or_create(
    slug="localai",
    defaults={
        "name": "LocalAI",
        "provider": provider,
        "meta_launch_url": "https://localai.{}/".format(os.environ["LOCALAI_DOMAIN"]),
        "meta_icon": "https://raw.githubusercontent.com/mudler/LocalAI/master/docs/static/favicon.svg",
        "group": "KI",
        "policy_engine_mode": "any",
    },
)
app.name = "LocalAI"
app.provider = provider
app.meta_launch_url = "https://localai.{}/".format(os.environ["LOCALAI_DOMAIN"])
app.meta_icon = "https://raw.githubusercontent.com/mudler/LocalAI/master/docs/static/favicon.svg"
app.group = "KI"
app.policy_engine_mode = "any"
app.save()
for order, group in enumerate((users, admins)):
    binding, _ = app.bindings.get_or_create(group=group, defaults={"order": order})
    if binding.order != order:
        binding.order = order
        binding.save(update_fields=["order"])
keys = cache.keys(user_app_cache_key("*")) or []
cache.delete_many(keys)
print("LocalAI OIDC provider, application, groups and access bindings are configured.")
' >/dev/null

printf '%s\n' 'LocalAI OIDC-Konfiguration wurde eingerichtet, ohne das Client-Secret auszugeben.'
