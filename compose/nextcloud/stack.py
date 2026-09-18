AUTH_GROUPS = ['nextcloud-admins', 'nextcloud-users']

TITLE = 'nextcloud'
REQUIRES = ['core']
APPLICATIONS = [{'groups': ['nextcloud-users', 'nextcloud-admins'],
  'icon': 'https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/png/nextcloud.png',
  'routers': ['nextcloud'],
  'slug': 'nextcloud',
  'title': 'nextcloud'},
 {'groups': ['nextcloud-users', 'nextcloud-admins'],
  'icon': 'https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/png/nextcloud.png',
  'routers': ['onlyoffice'],
  'slug': 'onlyoffice',
  'title': 'onlyoffice'}]
