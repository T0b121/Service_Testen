AUTH_GROUPS = ['partdb-admin', 'partdb-editor', 'partdb-readonly']

TITLE = 'partdb'
REQUIRES = ['core']
APPLICATIONS = [{'groups': ['partdb-admin', 'partdb-editor', 'partdb-readonly'],
  'icon': 'https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/png/part-db.png',
  'routers': ['partdb'],
  'slug': 'partdb',
  'title': 'partdb'}]
SSO = {'type': 'saml', 'slug': 'partdb-sso', 'application': 'partdb', 'acs': '/saml/acs', 'audience': '/sp'}
