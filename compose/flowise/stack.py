AUTH_GROUPS = ['flowise-admins', 'flowise-users']

TITLE = 'flowise'
REQUIRES = ['core', 'litellm', 'qdrant', 'neo4j']
APPLICATIONS = [{'groups': ['flowise-users', 'flowise-admins'],
  'icon': 'https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/png/flowise.png',
  'routers': ['flowise'],
  'slug': 'flowise',
  'title': 'flowise'}]


def before_start(context):
    from _manager.docker import run
    data = context.docker.config('flowise')
    volume = data['volumes']['flowise_data']['name']
    run(['docker', 'run', '--rm', '--network', 'none', '-v', volume + ':/data',
         'alpine:3.24', 'chown', '1000:1000', '/data'])
