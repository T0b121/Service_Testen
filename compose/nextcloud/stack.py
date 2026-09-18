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

SSO = {'type': 'oidc', 'slug': 'nextcloud', 'client_id_env': None,
       'secret': 'nextcloud_oidc_client_secret', 'callback': '/apps/user_oidc/code', 'application': 'nextcloud'}


def after_start(context):
    from _manager.config import read_env
    import json
    domain = read_env(context.stacks['nextcloud'].path / '.env')['DOMAIN']
    def occ(*args):
        return context.docker.compose('nextcloud', 'exec', '-T', '-u', 'www-data',
                                      'nextcloud', 'php', 'occ', *args)
    apps = json.loads(occ('app:list', '--output=json'))
    if 'user_oidc' not in apps.get('enabled', {}):
        if 'user_oidc' not in apps.get('disabled', {}): occ('app:install', 'user_oidc')
        else: occ('app:enable', 'user_oidc')
    occ('user_oidc:provider', 'Authentik', '--clientid=nextcloud',
        '--clientsecret-file=/run/secrets/nextcloud_oidc_client_secret',
        '--discoveryuri=https://auth.' + domain + '/application/o/nextcloud/.well-known/openid-configuration',
        '--scope=openid email profile groups', '--unique-uid=0', '--mapping-uid=preferred_username',
        '--mapping-display-name=name', '--mapping-email=email', '--group-provisioning=1', '--mapping-groups=groups')


def sync_user(context, action, user):
    import json
    def occ(*args):
        return context.docker.compose('nextcloud', 'exec', '-T', '-u', 'www-data', 'nextcloud', 'php', 'occ', *args)
    existing = json.loads(occ('user:list', '--output=json'))
    if user['username'] not in existing: return
    names = {g['name'] for g in context.auth.items('core/groups/') if g['pk'] in user.get('groups', [])}
    if action == 'delete' or not user['is_active'] or not names.intersection(AUTH_GROUPS):
        occ('user:disable', user['username'])
    else:
        occ('user:enable', user['username'])
        info = json.loads(occ('user:info', user['username'], '--output=json'))
        is_admin = 'admin' in info.get('groups', [])
        if ('nextcloud-admins' in names) != is_admin:
            occ('group:adduser' if not is_admin else 'group:removeuser', 'admin', user['username'])
