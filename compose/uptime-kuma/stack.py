AUTH_GROUPS = ['uptime-kuma-admins', 'uptime-kuma-users']

TITLE = 'uptime-kuma'
REQUIRES = ['core']
APPLICATIONS = [{'groups': ['uptime-kuma-users', 'uptime-kuma-admins'],
  'icon': 'https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/png/uptime-kuma.png',
  'routers': ['uptime-kuma'],
  'slug': 'uptime-kuma',
  'title': 'uptime-kuma'}]
