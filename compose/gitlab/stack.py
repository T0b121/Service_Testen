AUTH_GROUPS = ['gitlab-admins', 'gitlab-users']

TITLE = 'gitlab'
REQUIRES = ['core']
APPLICATIONS = [{'groups': ['gitlab-users', 'gitlab-admins'],
  'icon': 'https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/png/gitlab.png',
  'routers': ['gitlab'],
  'slug': 'gitlab',
  'title': 'gitlab'}]
SSO = {'type': 'oidc', 'slug': 'gitlab', 'client_id_env': 'GITLAB_OIDC_CLIENT_ID', 'secret': 'gitlab_oidc_client_secret', 'callback': '/users/auth/openid_connect/callback', 'application': 'gitlab'}


def after_start(context):
    context.docker.exec('gitlab', 'gitlab', 'gitlab-rails', 'runner',
        'ApplicationSetting.current.update!(signup_enabled: false)')

START_TIMEOUT = 1500


def sync_user(context, action, user):
    # Bestehende SSO-Konten werden anhand ihres stabilen OIDC-sub zugeordnet.
    # JIT-Kontoanlage erfolgt weiter beim ersten Login; Löschung sperrt lokale
    # Konten, damit Projekte und Beiträge erhalten bleiben.
    import json
    groups = {g['pk']: g['name'] for g in context.auth.items('core/groups/')}
    names = {groups[g] for g in user.get('groups', []) if g in groups}
    payload = dict(user, action=action, allowed=bool(names & set(AUTH_GROUPS)), admin='gitlab-admins' in names)
    script = '''require 'json'
p = JSON.parse(STDIN.read)
identity = Identity.find_by(provider: 'openid_connect', extern_uid: p['pk'].to_s)
u = identity&.user
if u
  if p['action'] == 'delete' || !p['is_active'] || !p['allowed']
    u.block! unless u.blocked?
  else
    u.update!(name: p['name'], email: p['email'], admin: p['admin'])
    u.activate! if u.blocked?
  end
end
'''
    # stdin contains data; Ruby source itself is fixed, never user interpolation.
    context.docker.exec('gitlab', 'gitlab', 'gitlab-rails', 'runner', script, input=json.dumps(payload))
