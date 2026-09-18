AUTH_GROUPS = ['ollama-admins', 'ollama-users']

TITLE = 'ollama'
REQUIRES = ['core']
APPLICATIONS = [{'groups': ['ollama-users', 'ollama-admins'],
  'icon': 'https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/png/ollama.png',
  'routers': ['ollama'],
  'slug': 'ollama',
  'title': 'ollama'}]
