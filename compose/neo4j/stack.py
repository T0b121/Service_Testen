AUTH_GROUPS = ['neo4j-admins', 'neo4j-users']

TITLE = 'neo4j'
REQUIRES = ['core']
APPLICATIONS = [{'groups': ['neo4j-users', 'neo4j-admins'],
  'icon': 'https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/png/neo4j.png',
  'routers': ['neo4j'],
  'slug': 'neo4j',
  'title': 'neo4j'}]
