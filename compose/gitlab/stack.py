AUTH_GROUPS = ['gitlab-admins', 'gitlab-users']

TITLE = 'gitlab'
REQUIRES = ['core']
APPLICATIONS = [{'groups': ['gitlab-users', 'gitlab-admins'],
  'icon': 'https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/png/gitlab.png',
  'routers': ['gitlab'],
  'slug': 'gitlab',
  'title': 'gitlab'}]
SSO = {'type': 'oidc', 'slug': 'gitlab', 'client_id_env': 'GITLAB_OIDC_CLIENT_ID', 'secret': 'gitlab_oidc_client_secret', 'callback': '/users/auth/openid_connect/callback', 'application': 'gitlab'}
