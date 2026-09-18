AUTH_GROUPS = ['localai-admins', 'localai-users']

TITLE = 'localai'
REQUIRES = ['core']
APPLICATIONS = [{'groups': ['localai-users', 'localai-admins'],
  'icon': 'https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/png/localai.png',
  'routers': ['localai'],
  'slug': 'localai',
  'title': 'localai'}]
SSO = {'type': 'oidc', 'slug': 'localai', 'client_id_env': None, 'secret': 'localai_oidc_client_secret', 'callback': '/api/auth/oidc/callback', 'application': 'localai'}
