#!/usr/bin/env bash
set -euo pipefail

stack_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$stack_dir"

set -a
# shellcheck disable=SC1091
. ./.env
set +a

client_secret=$(<secrets/paperless_oidc_client_secret)
provider_config=secrets/paperless_socialaccount_providers

docker exec \
  -e PAPERLESS_CLIENT_SECRET="$client_secret" \
  -e PAPERLESS_DOMAIN="$DOMAIN" \
  core-authentik-server ak shell -c '
import os
from authentik.core.models import Application, Group
from authentik.providers.oauth2.models import OAuth2Provider, ScopeMapping

users, _ = Group.objects.get_or_create(name="paperless-users")
admins, _ = Group.objects.get_or_create(name="paperless-admins")
gitlab_users = Group.objects.get(name="gitlab-users")
gitlab_admins = Group.objects.get(name="gitlab-admins")
users.users.add(*gitlab_users.users.all())
admins.users.add(*gitlab_admins.users.all())

group_mapping, _ = ScopeMapping.objects.get_or_create(
    name="Paperless OAuth Mapping: groups",
    defaults={
        "scope_name": "groups",
        "expression": "return {\"groups\": list(request.user.groups.values_list(\"name\", flat=True))}",
    },
)

template = Application.objects.get(slug="gitlab").provider.oauth2provider
defaults = {
    "client_id": "paperless",
    "client_secret": os.environ["PAPERLESS_CLIENT_SECRET"],
    "client_type": "confidential",
    "authentication_flow": template.authentication_flow,
    "authorization_flow": template.authorization_flow,
    "grant_types": ["authorization_code"],
    "access_code_validity": template.access_code_validity,
    "access_token_validity": template.access_token_validity,
    "refresh_token_validity": template.refresh_token_validity,
    "include_claims_in_id_token": True,
    "sub_mode": template.sub_mode,
    "issuer_mode": template.issuer_mode,
    "logout_method": template.logout_method,
    "_redirect_uris": [{
        "url": "https://paperless.{}/accounts/oidc/authentik/login/callback/".format(os.environ["PAPERLESS_DOMAIN"]),
        "matching_mode": "strict",
        "redirect_uri_type": "authorization",
    }],
}
provider, created = OAuth2Provider.objects.get_or_create(
    name="Paperless OIDC Provider", defaults=defaults
)
if not created:
    for field, value in defaults.items():
        setattr(provider, field, value)
    provider.save()
provider.property_mappings.set(list(template.property_mappings.all()) + [group_mapping])

app, _ = Application.objects.get_or_create(
    slug="paperless",
    defaults={
        "name": "Paperless",
        "provider": provider,
        "meta_launch_url": "https://paperless.{}/".format(os.environ["PAPERLESS_DOMAIN"]),
        "meta_icon": "https://cdn.simpleicons.org/paperlessngx/17541F",
        "policy_engine_mode": "any",
    },
)
app.name = "Paperless"
app.provider = provider
app.meta_launch_url = "https://paperless.{}/".format(os.environ["PAPERLESS_DOMAIN"])
app.meta_icon = "https://cdn.simpleicons.org/paperlessngx/17541F"
app.policy_engine_mode = "any"
app.save()
for order, group in enumerate((users, admins)):
    binding, _ = app.bindings.get_or_create(group=group, defaults={"order": order})
    if binding.order != order:
        binding.order = order
        binding.save(update_fields=["order"])
print("Paperless OIDC provider, application, groups and access bindings are configured.")
' >/dev/null

printf '%s' '{"openid_connect":{"APPS":[{"provider_id":"authentik","name":"Authentik","client_id":"paperless","secret":"' \
  > "$provider_config"
printf '%s' "$client_secret" >> "$provider_config"
printf '%s' '","settings":{"server_url":"https://auth.' >> "$provider_config"
printf '%s' "$DOMAIN" >> "$provider_config"
printf '%s\n' '/application/o/paperless/.well-known/openid-configuration","token_auth_method":"client_secret_post"}}],"SCOPE":["openid","profile","email","groups"]}}' >> "$provider_config"
chmod 600 "$provider_config"

printf '%s\n' 'Paperless OIDC configuration has been written without exposing its secret.'
