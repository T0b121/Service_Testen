import json
import os
import re
import shutil
import subprocess
from .model import ManagerError, order


def run(args, *, input=None, timeout=600):
    try:
        result = subprocess.run(args, input=input, capture_output=True, text=True, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired) as error:
        raise ManagerError(f'{args[0]} konnte nicht ausgeführt werden oder hat das Zeitlimit überschritten.') from error
    if result.returncode:
        # Docker-Fehler können aufgelöste Secrets enthalten; nicht ungefiltert ausgeben.
        raise ManagerError(f'{args[0]} fehlgeschlagen (Exit {result.returncode}); Dienststatus lokal prüfen.')
    return result.stdout


class Docker:
    def __init__(self, stacks):
        self.stacks = stacks

    def check(self):
        if not shutil.which('docker'):
            raise ManagerError('Docker fehlt. Docker Engine und Compose Plugin installieren.')
        run(['docker', 'info', '--format', '{{.ServerVersion}}'], timeout=30)
        run(['docker', 'compose', 'version'], timeout=30)

    def compose(self, name, *args, input=None, timeout=600):
        path = self.stacks[name].path
        return run(['docker', 'compose', '--project-directory', str(path), '--env-file', str(path / '.env'),
                    '-p', name, '-f', str(path / 'compose.yml'), *args], input=input, timeout=timeout)

    def config(self, name):
        return json.loads(self.compose(name, 'config', '--format', 'json'))

    def resources(self, name):
        data = self.config(name)
        for kind in ('networks', 'volumes'):
            singular = kind[:-1]
            for key, spec in data.get(kind, {}).items():
                if not spec.get('external'):
                    continue
                resource = spec.get('name', key)
                try:
                    run(['docker', singular, 'inspect', resource], timeout=30)
                except ManagerError:
                    run(['docker', singular, 'create', '--label', 'stack-manager.managed=true', resource], timeout=30)
        return data

    def start(self, selected):
        for name in order(self.stacks, selected):
            data = self.resources(name)
            validate_exposure(name, data)
            self.compose(name, 'up', '-d', '--wait', '--wait-timeout', str(getattr(self.stacks[name].module, 'START_TIMEOUT', 300)))

    def stop(self, selected):
        for name in reversed(order(self.stacks, selected)):
            self.compose(name, 'stop')

    def exec(self, name, service, *command, input=None):
        return self.compose(name, 'exec', '-T', service, *command, input=input)


def labels(service):
    value = service.get('labels', {})
    return value if isinstance(value, dict) else dict(x.split('=', 1) for x in value)


def routes(data):
    result = {}
    for service, spec in data['services'].items():
        values = labels(spec)
        for key, value in values.items():
            match = re.fullmatch(r'traefik\.http\.routers\.([^.]+)\.rule', key)
            if match:
                router = match[1]
                result[router] = {'service': service, 'rule': value,
                                  'middlewares': values.get(f'traefik.http.routers.{router}.middlewares', '')}
    return result


def infrastructure_route(stack, router, route):
    if stack == 'core' and router == 'authentik' and route['service'] == 'authentik-server':
        return True
    # Nur explizite Outpost-Pfade dürfen die Authentifizierung umgehen.
    rule = route['rule']
    return (router.startswith('authentik-outpost') and '||' not in rule
            and re.fullmatch(r'Host\(`[^`]+`\) && PathPrefix\(`/outpost.goauthentik.io/`\)', rule) is not None)


def validate_exposure(name, data):
    for service, spec in data['services'].items():
        if spec.get('network_mode') == 'host':
            raise ManagerError(f'{name}/{service}: Host-Netzwerk umgeht Forward Auth.')
        if spec.get('ports') and not (name == 'core' and service == 'traefik'):
            raise ManagerError(f'{name}/{service}: veröffentlichte Host-Ports sind nicht zulässig.')
        if any(k.startswith(('traefik.tcp.', 'traefik.udp.')) for k in labels(spec)):
            raise ManagerError(f'{name}/{service}: TCP/UDP-Router können kein Forward Auth verwenden.')
    for router, route in routes(data).items():
        if infrastructure_route(name, router, route):
            continue
        chain = route['middlewares'].split(',')
        if not any(x in chain for x in ('authentik', 'authentik@docker')):
            raise ManagerError(f'{name}/{router}: verpflichtendes Forward Auth fehlt.')
