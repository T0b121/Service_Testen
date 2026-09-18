AUTH_GROUPS = ['core-admins']

TITLE = 'core'
REQUIRES = []
APPLICATIONS = [{'groups': ['core-admins'],
  'icon': 'https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/png/traefik.png',
  'routers': ['traefik-dashboard'],
  'slug': 'core',
  'title': 'traefik-dashboard'}]
