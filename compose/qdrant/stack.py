AUTH_GROUPS = ['qdrant-admins', 'qdrant-users']

TITLE = 'qdrant'
REQUIRES = ['core']
APPLICATIONS = [{'groups': ['qdrant-users', 'qdrant-admins'],
  'icon': 'https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/png/qdrant.png',
  'routers': ['qdrant'],
  'slug': 'qdrant',
  'title': 'qdrant'}]
