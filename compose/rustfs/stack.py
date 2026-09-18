AUTH_GROUPS = ['rustfs-admins', 'rustfs-users']

TITLE = 'rustfs'
REQUIRES = ['core']
APPLICATIONS = [{'groups': ['rustfs-users', 'rustfs-admins'],
  'icon': 'https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/png/rustfs.png',
  'routers': ['rustfs', 'rustfs-console'],
  'slug': 'rustfs',
  'title': 'rustfs'}]
SSO = {'type': 'oidc', 'slug': 'rustfs-console', 'client_id_env': 'RUSTFS_OIDC_CLIENT_ID', 'secret': 'rustfs_oidc_client_secret', 'callback': '/rustfs/admin/v3/oidc/callback/default', 'application': 'rustfs'}
