#!/usr/bin/env bash
set -euo pipefail

stack_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${stack_dir}"

set -a
# shellcheck disable=SC1091
. ./.env
set +a

docker exec -e COMFYUI_DOMAIN="${DOMAIN}" core-authentik-server ak shell -c '
import os
from django.core.cache import cache
from authentik.core.api.applications import user_app_cache_key
from authentik.core.models import Application, Group
from authentik.outposts.models import Outpost
from authentik.providers.proxy.models import ProxyProvider

users, _ = Group.objects.get_or_create(name="comfyui-users")
admins, _ = Group.objects.get_or_create(name="comfyui-admins")
gitlab_users = Group.objects.get(name="gitlab-users")
gitlab_admins = Group.objects.get(name="gitlab-admins")
users.users.add(*gitlab_users.users.all())
admins.users.add(*gitlab_admins.users.all())

template = ProxyProvider.objects.get(name="Flowise Access Provider")
defaults = {
    "external_host": "https://comfyui.{}/".format(os.environ["COMFYUI_DOMAIN"]),
    "internal_host": template.internal_host,
    "mode": template.mode,
    "grant_types": template.grant_types,
    "intercept_header_auth": template.intercept_header_auth,
    "authorization_flow": template.authorization_flow,
    "authentication_flow": template.authentication_flow,
    "_redirect_uris": [
        {
            "url": "https://comfyui.{}/outpost.goauthentik.io/callback?X-authentik-auth-callback=true".format(os.environ["COMFYUI_DOMAIN"]),
            "matching_mode": "strict",
            "redirect_uri_type": "authorization",
        },
        {
            "url": "https://comfyui.{}/?X-authentik-auth-callback=true".format(os.environ["COMFYUI_DOMAIN"]),
            "matching_mode": "strict",
            "redirect_uri_type": "authorization",
        },
    ],
}
provider, created = ProxyProvider.objects.get_or_create(
    name="ComfyUI Access Provider", defaults=defaults
)
if not created:
    for field, value in defaults.items():
        setattr(provider, field, value)
    provider.save()
outpost = Outpost.objects.get(providers=template)
outpost.providers.add(provider)

app, _ = Application.objects.get_or_create(
    slug="comfyui",
    defaults={
        "name": "ComfyUI",
        "provider": provider,
        "meta_launch_url": "https://comfyui.{}/".format(os.environ["COMFYUI_DOMAIN"]),
        "meta_icon": "https://docs.comfy.org/favicon.ico",
        "group": "KI",
        "policy_engine_mode": "any",
    },
)
app.name = "ComfyUI"
app.provider = provider
app.meta_launch_url = "https://comfyui.{}/".format(os.environ["COMFYUI_DOMAIN"])
app.meta_icon = "https://docs.comfy.org/favicon.ico"
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
print("ComfyUI access provider, application, groups and access bindings are configured.")
' >/dev/null

printf '%s\n' 'ComfyUI Authentik-Zugriff wurde eingerichtet.'
