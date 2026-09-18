AUTH_GROUPS = ['flowise-admins', 'flowise-users']

TITLE = 'flowise'
REQUIRES = ['core', 'litellm', 'qdrant', 'neo4j']
APPLICATIONS = [{'groups': ['flowise-users', 'flowise-admins'],
  'icon': 'https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/png/flowise.png',
  'routers': ['flowise'],
  'slug': 'flowise',
  'title': 'flowise'}]
