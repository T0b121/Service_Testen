"""Authentik API über den lokalen Servercontainer, ohne öffentliche Bootstrap-Route."""
import base64
import hashlib
import json
import re
import secrets
import time
from urllib.request import urlopen
from .config import read_env
from .docker import routes, infrastructure_route
from .model import ManagerError
from .state import private_write

# Token wird erst im Container aus dem gemounteten Secret gelesen.
API_SCRIPT = '''import sys,json,urllib.request,urllib.error
from pathlib import Path
p=json.load(sys.stdin)
token=Path('/run/secrets/manager_api_token').read_text().strip()
body=p.get('body')
headers={'Authorization':'Bearer '+token,'Content-Type':p.get('content_type','application/json')}
data=__import__('base64').b64decode(p['raw']) if 'raw' in p else (json.dumps(body).encode() if body is not None else None)
r=urllib.request.Request('http://127.0.0.1:9000/api/v3/'+p['path'],data=data,headers=headers,method=p['method'])
try:
 with urllib.request.urlopen(r,timeout=30) as f:
  raw=f.read().decode(); print(json.dumps({'ok':True,'data':json.loads(raw) if raw else {}}))
except urllib.error.HTTPError as e:
 print(json.dumps({'ok':False,'status':e.code}))
'''


class Authentik:
    def __init__(self, docker, state):
        self.docker, self.state = docker, state

    def request(self, method, path, body=None, raw=None, content_type=None):
        if path.startswith(('http', '/')) or '..' in path:
            raise ManagerError('Ungültiger API-Pfad.')
        payload = {'method': method, 'path': path, 'body': body}
        if raw is not None:
            payload.update(raw=base64.b64encode(raw).decode(), content_type=content_type)
        try:
            response = json.loads(self.docker.exec('core', 'authentik-server', 'python', '-c', API_SCRIPT,
                                                  input=json.dumps(payload)))
        except (ValueError, KeyError) as error:
            raise ManagerError('Ungültige Antwort der Authentik-API.') from error
        if not response.get('ok'):
            raise ManagerError(f'Authentik: {method} {path.split("?")[0]} fehlgeschlagen (HTTP {response.get("status")}).')
        return response['data']

    def items(self, path):
        items, page = [], 1
        while True:
            result = self.request('GET', path + ('&' if '?' in path else '?') + f'page_size=100&page={page}')
            items.extend(result['results'])
            if not result.get('pagination', {}).get('next'):
                return items
            page += 1

    def ensure(self, path, match, payload, *, id_field='pk'):
        existing = [x for x in self.items(path) if all(x.get(k) == v for k, v in match.items())]
        if len(existing) > 1:
            raise ManagerError(f'Authentik: mehrdeutiges Objekt unter {path}')
        if existing:
            return self.request('PATCH', f'{path}{existing[0][id_field]}/', payload)
        return self.request('POST', path, {**match, **payload})

    def flow(self, slug):
        found = [x for x in self.items('flows/instances/') if x['slug'] == slug]
        if len(found) != 1:
            raise ManagerError(f'Authentik-Standardflow fehlt: {slug}')
        return found[0]['pk']

    def wait(self):
        for attempt in range(90):
            try:
                self.items('core/groups/')
                return
            except ManagerError:
                time.sleep(2)
        raise ManagerError('Authentik-Verwaltungszugriff nach 180 Sekunden nicht bereit.')

    def groups(self, stack):
        return {name: self.ensure('core/groups/', {'name': name}, {'is_superuser': False})['pk'] for name in stack.groups}

    def application(self, stack, slug, title, provider, url, group_ids, icon=None):
        app = self.ensure('core/applications/', {'slug': slug}, {
            'name': title, 'provider': provider, 'meta_launch_url': url,
            'group': stack.title, 'policy_engine_mode': 'any'}, id_field='slug')
        bindings = [b for b in self.items('policies/bindings/') if b['target'] == app['pk']]
        # Diese Anwendung gehört dem Manager: fremde Freigaben nicht still übernehmen.
        if any(b.get('group') not in group_ids or b.get('user') or b.get('policy') for b in bindings):
            raise ManagerError(f'{slug}: unerwartete Zugriffsbindung; vor Fortsetzung prüfen.')
        for i, group in enumerate(group_ids):
            self.ensure('policies/bindings/', {'target': app['pk'], 'group': group},
                        {'order': i, 'enabled': True, 'negate': False, 'timeout': 30})
        self.state.data['objects'][slug] = app['pk']
        self.state.save()
        if icon:
            self.icon(slug, icon)
        return app

    def forward_auth(self, stack):
        data = self.docker.config(stack.name)
        all_routes = routes(data)
        group_ids = self.groups(stack)
        providers = []
        declared = {router: app for app in stack.applications for router in app['routers']}
        hosts = {}
        for router, route in all_routes.items():
            if infrastructure_route(stack.name, router, route):
                continue
            if router not in declared:
                raise ManagerError(f'{stack.name}: keine Gruppenbeschreibung für Router {router}')
            matches = re.findall(r'Host\(`([^`]+)`\)', route['rule'])
            if len(matches) != 1:
                raise ManagerError(f'{router}: genau ein Host-Ausdruck erforderlich')
            app = declared[router]
            if matches[0] in hosts and hosts[matches[0]] != app:
                raise ManagerError('Verschiedene Zugriffsgruppen für denselben Host sind nicht unterstützt.')
            hosts[matches[0]] = app
        for host, app in hosts.items():
            slug = f'{app["slug"]}-access'
            provider = self.ensure('providers/proxy/', {'name': f'stack-manager:{slug}'}, {
                'mode': 'forward_single', 'external_host': f'https://{host}',
                'authorization_flow': self.flow('default-provider-authorization-implicit-consent'),
                'invalidation_flow': self.flow('default-provider-invalidation-flow')})
            self.application(stack, slug, app['title'], provider['pk'], f'https://{host}',
                             [group_ids[g] for g in app['groups']], app.get('icon'))
            providers.append(provider['pk'])
        outposts = [o for o in self.items('outposts/instances/') if o.get('managed') == 'goauthentik.io/outposts/embedded']
        if len(outposts) != 1:
            raise ManagerError('Authentik Embedded Outpost nicht eindeutig gefunden.')
        outpost = outposts[0]
        domain = read_env(stack.path / '.env')['DOMAIN']
        config = dict(outpost.get('config') or {})
        config.update(authentik_host=f'https://auth.{domain}', authentik_host_browser=f'https://auth.{domain}')
        self.request('PATCH', f'outposts/instances/{outpost["pk"]}/', {
            'providers': sorted(set(outpost['providers']) | set(providers)), 'config': config})

    def icon(self, slug, url):
        cache = self.state.directory.parent / '_cache' / 'icons'
        cache.mkdir(parents=True, exist_ok=True, mode=0o700)
        path = cache / (hashlib.sha256(url.encode()).hexdigest() + '.png')
        try:
            if not path.exists():
                if not url.startswith('https://'):
                    raise ValueError('Icon-Quelle muss HTTPS sein')
                with urlopen(url, timeout=20) as response:
                    if not response.url.startswith('https://'):
                        raise ValueError('Unsicheres Redirect')
                    data = response.read(2 * 1024 * 1024 + 1)
                if len(data) > 2 * 1024 * 1024 or not data.startswith(b'\x89PNG\r\n\x1a\n'):
                    raise ValueError('Kein gültiges PNG oder Datei zu groß')
                path.write_bytes(data)
            data = path.read_bytes()
            filename = 'stack-manager-' + hashlib.sha256(data).hexdigest() + '.png'
            existing = self.request('GET', 'admin/file/?usage=media')
            if not any(x['name'] == filename for x in existing):
                boundary = 'stackmanager' + secrets.token_hex(12)
                body = (f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="{filename}"\r\n'
                        'Content-Type: image/png\r\n\r\n').encode() + data + f'\r\n--{boundary}--\r\n'.encode()
                self.request('POST', 'admin/file/', raw=body,
                             content_type=f'multipart/form-data; boundary={boundary}')
            self.request('PATCH', f'core/applications/{slug}/', {'meta_icon': filename})
            self.state.data['pending'].pop('icon:' + slug, None)
        except (OSError, ValueError, ManagerError):
            # Ohne Icon bleibt Authentiks Standardicon erhalten.
            self.state.data['pending']['icon:' + slug] = 'Standardicon aktiv; Download/Upload erneut versuchen.'
        self.state.save()


def bootstrap_files(core, state):
    token = core.path / 'secrets' / 'manager_api_token'
    password = core.path / 'secrets' / 'manager_bootstrap_password'
    if 'auth-bootstrap' in state.data['completed']:
        if not token.exists():
            raise ManagerError('Verwaltungstoken fehlt; kein neues Bootstrap-Token für bestehende Installation erzeugen.')
        return
    if not token.exists():
        private_write(token, secrets.token_urlsafe(48))
    if not password.exists():
        private_write(password, secrets.token_urlsafe(24))


def finish_bootstrap(core, state, auth):
    auth.wait()
    if 'auth-bootstrap' in state.data['completed']:
        return
    path = core.path / 'secrets' / 'manager_bootstrap_password'
    print('\nAuthentik-Erstzugang – jetzt im Passwortmanager speichern:')
    print('Benutzername: akadmin')
    print('Passwort: ' + path.read_text())
    input('Mit Enter bestätigen, dass der Zugang gespeichert ist: ')
    state.data['completed'].append('auth-bootstrap')
    state.save()
    path.unlink(missing_ok=True)
