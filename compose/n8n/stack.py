AUTH_GROUPS = ['n8n-admins', 'n8n-users']

TITLE = 'n8n'
REQUIRES = ['core', 'litellm', 'qdrant', 'neo4j', 'searxng']
APPLICATIONS = [{'groups': ['n8n-users', 'n8n-admins'],
  'icon': 'https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/png/n8n.png',
  'routers': ['n8n'],
  'slug': 'n8n',
  'title': 'n8n'}]
