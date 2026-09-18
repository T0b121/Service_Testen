AUTH_GROUPS = ['paperless-admins', 'paperless-users']

TITLE = 'paperless'
REQUIRES = ['core']
APPLICATIONS = [{'groups': ['paperless-users', 'paperless-admins'],
  'icon': 'https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/png/paperless.png',
  'routers': ['paperless'],
  'slug': 'paperless',
  'title': 'paperless'}]
SSO = {'type': 'oidc', 'slug': 'paperless', 'client_id_env': None, 'secret': 'paperless_oidc_client_secret', 'callback': '/accounts/oidc/authentik/login/callback/', 'application': 'paperless'}
