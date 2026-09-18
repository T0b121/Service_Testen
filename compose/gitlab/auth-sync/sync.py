#!/usr/bin/env python3
"""Synchronise Authentik GitLab groups to existing GitLab OIDC accounts."""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


AUTHENTIK_URL = os.environ["AUTHENTIK_URL"].rstrip("/")
GITLAB_URL = os.environ["GITLAB_URL"].rstrip("/")
USERS_GROUP = os.environ.get("AUTHENTIK_USERS_GROUP", "gitlab-users")
ADMINS_GROUP = os.environ.get("AUTHENTIK_ADMINS_GROUP", "gitlab-admins")
POLL_SECONDS = max(60, int(os.environ.get("POLL_SECONDS", "300")))
AUTHENTIK_TOKEN = Path("/run/secrets/authentik_gitlab_sync_api_token").read_text().strip()
GITLAB_TOKEN = Path("/run/secrets/gitlab_auth_sync_api_token").read_text().strip()


def log(message: str) -> None:
    print(message, flush=True)


def request_json(url: str, *, headers: dict[str, str], method: str = "GET", data: dict[str, Any] | None = None) -> Any:
    body = urlencode(data).encode() if data is not None else None
    request = Request(url, data=body, headers=headers, method=method)
    try:
        with urlopen(request, timeout=20) as response:
            payload = response.read().decode()
    except HTTPError as error:
        detail = error.read().decode(errors="replace")[:400]
        raise RuntimeError(f"HTTP {error.code} for {method} {url}: {detail}") from error
    except URLError as error:
        raise RuntimeError(f"request failed for {method} {url}: {error.reason}") from error
    return json.loads(payload) if payload else None


def paginated(url: str, headers: dict[str, str]) -> list[dict[str, Any]]:
    separator = "&" if "?" in url else "?"
    next_url: str | None = f"{url}{separator}page_size=100"
    results: list[dict[str, Any]] = []
    while next_url:
        page = request_json(next_url, headers=headers)
        if isinstance(page, list):
            results.extend(page)
            break
        results.extend(page.get("results", []))
        next_url = page.get("pagination", {}).get("next")
    return results


def authentik_members() -> tuple[set[str], set[str]]:
    headers = {"Authorization": f"Bearer {AUTHENTIK_TOKEN}", "Accept": "application/json"}
    groups = {group["name"]: set(group.get("users", [])) for group in paginated(f"{AUTHENTIK_URL}/api/v3/core/groups/", headers)}
    missing = [name for name in (USERS_GROUP, ADMINS_GROUP) if name not in groups]
    if missing:
        raise RuntimeError("Authentik groups missing: " + ", ".join(missing))
    users = {str(user.get("pk", user.get("uuid"))): user["username"] for user in paginated(f"{AUTHENTIK_URL}/api/v3/core/users/", headers)}

    def usernames(group: str) -> set[str]:
        absent = [str(pk) for pk in groups[group] if str(pk) not in users]
        if absent:
            raise RuntimeError(f"could not resolve {len(absent)} member(s) of {group}")
        return {users[str(pk)] for pk in groups[group]}

    return usernames(USERS_GROUP), usernames(ADMINS_GROUP)


def gitlab_request(path: str, *, method: str = "GET", data: dict[str, Any] | None = None) -> Any:
    return request_json(
        f"{GITLAB_URL}/api/v4{path}",
        headers={"PRIVATE-TOKEN": GITLAB_TOKEN, "Accept": "application/json"},
        method=method,
        data=data,
    )


def is_oidc_user(user_id: int) -> bool:
    detail = gitlab_request(f"/users/{user_id}")
    return any(identity.get("provider") == "openid_connect" for identity in detail.get("identities", []))


def sync_once() -> None:
    members, admins = authentik_members()
    allowed = members | admins
    gitlab_users = paginated(
        f"{GITLAB_URL}/api/v4/users",
        {"PRIVATE-TOKEN": GITLAB_TOKEN, "Accept": "application/json"},
    )
    oidc_users = [user for user in gitlab_users if is_oidc_user(user["id"])]
    by_username = {user["username"]: user for user in oidc_users}
    changed = 0

    for username in sorted(allowed):
        user = by_username.get(username)
        if user is None:
            log(f"waiting for first OIDC login: {username}")
            continue
        desired_admin = username in admins
        if bool(user.get("is_admin")) != desired_admin:
            gitlab_request(f"/users/{user['id']}", method="PUT", data={"admin": str(desired_admin).lower()})
            changed += 1
        if user.get("state") == "blocked_pending_approval":
            gitlab_request(f"/users/{user['id']}/approve", method="POST")
            changed += 1
        elif user.get("state") == "blocked":
            gitlab_request(f"/users/{user['id']}/unblock", method="POST")
            changed += 1

    for user in oidc_users:
        if user["username"] in allowed:
            continue
        if user.get("state") != "blocked":
            gitlab_request(f"/users/{user['id']}/block", method="POST")
            changed += 1
        if user.get("is_admin"):
            gitlab_request(f"/users/{user['id']}", method="PUT", data={"admin": "false"})
            changed += 1

    log(f"sync complete: allowed={len(allowed)} admins={len(admins)} oidc_accounts={len(oidc_users)} changes={changed}")


def main() -> None:
    if not AUTHENTIK_TOKEN or not GITLAB_TOKEN:
        raise RuntimeError("API token secret is empty")
    while True:
        try:
            sync_once()
        except Exception as error:  # keep the service alive; never change state on a failed read
            log(f"sync failed: {error}")
        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        log(f"fatal: {error}")
        sys.exit(1)
