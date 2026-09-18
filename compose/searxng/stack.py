AUTH_GROUPS = ['searxng-admins', 'searxng-users']

TITLE = 'searxng'
REQUIRES = ['core']
APPLICATIONS = [{'groups': ['searxng-users', 'searxng-admins'],
  'icon': 'https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/png/searxng.png',
  'routers': ['searxng'],
  'slug': 'searxng',
  'title': 'searxng'}]
