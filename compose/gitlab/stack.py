AUTH_GROUPS = ['gitlab-admins', 'gitlab-users']

TITLE = 'gitlab'
REQUIRES = ['core']
APPLICATIONS = [{'groups': ['gitlab-users', 'gitlab-admins'],
  'icon': 'https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/png/gitlab.png',
  'routers': ['gitlab'],
  'slug': 'gitlab',
  'title': 'gitlab'}]
SSO = {'type': 'oidc', 'slug': 'gitlab', 'client_id_env': 'GITLAB_OIDC_CLIENT_ID', 'secret': 'gitlab_oidc_client_secret', 'callback': '/users/auth/openid_connect/callback', 'application': 'gitlab'}


def configure(context, config):
    from _manager.model import ManagerError
    key = 'gitlab.GITLAB_WEB_IDE_MARKETPLACE_FALLBACK'
    if key not in config.values:
        print('GitLab Web-IDE: Der Marketplace-Fallback erlaubt Erweiterungen,')
        print('wenn keine getrennte Origin für deren Ausführung verfügbar ist.')
        print('Ohne Fallback bleibt diese Trennung erforderlich; manche')
        print('Erweiterungen können dann nicht geladen werden. Standard: deaktiviert.')
        while True:
            answer = input('Web-IDE-Marketplace-Fallback erlauben? [j/N]: ').strip().lower()
            if answer in ('', 'n', 'nein', 'no', 'false'):
                config.values[key] = 'false'
                break
            if answer in ('j', 'ja', 'y', 'yes', 'true'):
                config.values[key] = 'true'
                break
            print('Bitte j oder n eingeben; Enter bedeutet Nein.')
    if config.values[key] not in ('true', 'false'):
        raise ManagerError('GITLAB_WEB_IDE_MARKETPLACE_FALLBACK muss true oder false sein.')


def after_start(context):
    import json
    from _manager.config import read_env
    from _manager.model import ManagerError
    value = read_env(context.stacks['gitlab'].path / '.env').get('GITLAB_WEB_IDE_MARKETPLACE_FALLBACK')
    if value not in ('true', 'false'):
        raise ManagerError('GitLab-Fallback-Auswahl fehlt oder ist ungültig; Einrichtung erneut ausführen.')
    # Keine externe Skriptdatei und kein zusätzlicher API-Token erforderlich.
    # Beide Application Settings gemeinsam setzen und die gespeicherten Werte prüfen.
    script = """require 'json'
desired = JSON.parse(STDIN.read)
settings = ApplicationSetting.current
settings.update!(desired)
settings.reload
desired.each do |key, value|
  raise "GitLab setting not applied: #{key}" unless settings.public_send(key) == value
end
"""
    context.docker.exec('gitlab', 'gitlab', 'gitlab-rails', 'runner', script,
        input=json.dumps({'signup_enabled': False,
            'vscode_extension_marketplace_single_origin_fallback_enabled': value == 'true'}))

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
