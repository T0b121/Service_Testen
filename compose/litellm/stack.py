AUTH_GROUPS = ['litellm-admins', 'litellm-users']

TITLE = 'litellm'
REQUIRES = ['core', 'langfuse', 'ollama', 'localai']
APPLICATIONS = [{'groups': ['litellm-users', 'litellm-admins'],
  'icon': 'https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/png/litellm.png',
  'routers': ['litellm-api', 'litellm'],
  'slug': 'litellm',
  'title': 'litellm-api'}]
SSO = {'type': 'oidc', 'slug': 'litellm', 'client_id_env': 'LITELLM_OIDC_CLIENT_ID', 'secret': 'LITELLM_OIDC_CLIENT_SECRET', 'callback': '/sso/callback', 'application': 'litellm'}
