AUTH_GROUPS = ['paperless-admins', 'paperless-users']

TITLE = 'paperless'
REQUIRES = ['core']
APPLICATIONS = [{'groups': ['paperless-users', 'paperless-admins'],
  'icon': 'https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/png/paperless.png',
  'routers': ['paperless'],
  'slug': 'paperless',
  'title': 'paperless'}]
SSO = {'type': 'oidc', 'slug': 'paperless', 'client_id_env': None, 'secret': 'paperless_oidc_client_secret', 'callback': '/accounts/oidc/authentik/login/callback/', 'application': 'paperless'}


def after_start(context):
    script = '''from django.contrib.auth.models import Group, Permission
permissions = Permission.objects.filter(content_type__app_label__in=('documents', 'paperless'))
for name in ('paperless-users', 'paperless-admins'):
    group, _ = Group.objects.get_or_create(name=name)
    group.permissions.set(permissions)
'''
    context.docker.exec('paperless', 'paperless', 'python3', '/usr/src/paperless/src/manage.py', 'shell', '-c', script)


def sync_user(context, action, user):
    import json
    names = [g['name'] for g in context.auth.items('core/groups/') if g['pk'] in user.get('groups', [])]
    data = dict(user, action=action, names=names)
    script = '''import json,sys
from allauth.socialaccount.models import SocialAccount
p=json.load(sys.stdin)
accounts=SocialAccount.objects.filter(provider='authentik', uid=str(p['pk'])).select_related('user')
for account in accounts:
    user=account.user
    user.is_active=p['action']!='delete' and p['is_active'] and bool(set(p['names']) & {'paperless-users','paperless-admins'})
    user.is_staff='paperless-admins' in p['names']
    user.is_superuser=user.is_staff
    user.email=p['email']
    user.save(update_fields=['is_active','is_staff','is_superuser','email'])
'''
    context.docker.exec('paperless', 'paperless', 'python3', '/usr/src/paperless/src/manage.py', 'shell', '-c', script,
                        input=json.dumps(data))
