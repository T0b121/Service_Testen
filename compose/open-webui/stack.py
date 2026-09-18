AUTH_GROUPS = ['open-webui-admins', 'open-webui-users']

TITLE = 'open-webui'
REQUIRES = ['core', 'litellm', 'searxng']
APPLICATIONS = [{'groups': ['open-webui-users', 'open-webui-admins'],
  'icon': 'https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/png/openwebui.png',
  'routers': ['open-webui'],
  'slug': 'open-webui',
  'title': 'open-webui'}]
SSO = {'type': 'oidc', 'slug': 'open-webui', 'client_id_env': 'OPENWEBUI_OIDC_CLIENT_ID', 'secret': 'OPENWEBUI_OIDC_CLIENT_SECRET', 'callback': '/oauth/oidc/callback', 'application': 'open-webui'}
