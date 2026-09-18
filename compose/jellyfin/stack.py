AUTH_GROUPS = ['jellyfin-admins', 'jellyfin-users']

TITLE = 'jellyfin'
REQUIRES = ['core']
APPLICATIONS = [{'groups': ['jellyfin-users', 'jellyfin-admins'],
  'icon': 'https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/png/jellyfin.png',
  'routers': ['jellyfin'],
  'slug': 'jellyfin',
  'title': 'jellyfin'}]
