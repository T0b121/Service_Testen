AUTH_GROUPS = ['langfuse-admins', 'langfuse-users']

TITLE = 'langfuse'
REQUIRES = ['core', 'rustfs']
APPLICATIONS = [{'groups': ['langfuse-users', 'langfuse-admins'],
  'icon': 'https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/png/langfuse.png',
  'routers': ['langfuse'],
  'slug': 'langfuse',
  'title': 'langfuse'}]
SSO = {'type': 'oidc', 'slug': 'langfuse', 'client_id_env': 'LANGFUSE_OIDC_CLIENT_ID', 'secret': 'LANGFUSE_OIDC_CLIENT_SECRET', 'callback': '/api/auth/callback/authentik', 'application': 'langfuse'}
