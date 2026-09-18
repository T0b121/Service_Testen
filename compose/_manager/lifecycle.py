from pathlib import Path
import re
from .auth import Authentik, bootstrap_files, finish_bootstrap
from .config import Configuration, parse, read_env
from .docker import Docker, validate_exposure
from .model import discover, order, ManagerError
from .sso import provision
from .state import State
from .permissions import ensure_secret_group, prepare_secrets


class Context:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.stacks = discover(self.root)
        self.state = State(self.root)
        self.docker = Docker(self.stacks)
        self.auth = Authentik(self.docker, self.state)

    def check_templates(self):
        import yaml
        for name, stack in self.stacks.items():
            entries = parse(name, (stack.path / '.env.example').read_text())
            text = (stack.path / 'compose.yml').read_text()
            variables = set(re.findall(r'(?<!\$)\$\{([A-Z][A-Z_0-9]*)', text))
            supplied = {e.variable for e in entries if e.mode != '-'}
            if variables - supplied:
                raise ManagerError(f'{name}: fehlende ENV-Vorlagen: {", ".join(sorted(variables - supplied))}')
            validate_exposure(name, yaml.safe_load(text))
        Configuration(self.stacks, list(self.stacks))

    def initialize(self, selected):
        selected = order(self.stacks, selected)
        self.check_templates()
        self.docker.check()
        ensure_secret_group()
        print('Einrichtungsreihenfolge: ' + ' → '.join(selected))
        cfg = Configuration(self.stacks, selected)
        cfg.collect()
        domain = cfg.values.get('global.DOMAIN', '')
        if not re.fullmatch(r'(?=.{1,253}$)[A-Za-z0-9](?:[A-Za-z0-9.-]*[A-Za-z0-9])?', domain) or '.' not in domain:
            raise ManagerError('DOMAIN muss ein DNS-Domainname ohne Schema oder Pfad sein.')
        cfg.write()
        bootstrap_files(self.stacks['core'], self.state)
        self.state.data['desired'] = selected
        self.state.save()
        prepare_secrets(self.stacks['core'])
        self.docker.start(['core'])
        finish_bootstrap(self.stacks['core'], self.state, self.auth)
        for name in selected:
            key = 'setup:' + name
            self.state.data['pending'][key] = 'Einrichtung noch nicht vollständig.'
            self.state.save()
            stack = self.stacks[name]
            self.docker.resources(name)
            self.auth.forward_auth(stack)
            provision(self.auth, stack)
            prepare_secrets(stack)
            hook = getattr(stack.module, 'before_start', None)
            if hook:
                hook(self)
            self.docker.compose(name, 'up', '-d', '--wait', '--wait-timeout',
                str(getattr(stack.module, 'START_TIMEOUT', 300)), timeout=getattr(stack.module, 'START_TIMEOUT', 300) + 120)
            hook = getattr(stack.module, 'after_start', None)
            if hook:
                hook(self)
            self.state.data['pending'].pop(key, None)
            if key not in self.state.data['completed']:
                self.state.data['completed'].append(key)
            self.state.save()
        old = self.state.data['selected']
        for name in reversed(order(self.stacks, old)):
            if name not in selected:
                self.docker.compose(name, 'stop')
        self.state.data['selected'] = selected
        self.state.data.pop('desired', None)
        self.state.save()

    def start(self):
        names = self.state.data['selected']
        if self.state.data.get('desired') or any('setup:' + n not in self.state.data['completed'] or 'setup:' + n in self.state.data['pending'] for n in names):
            raise ManagerError('Ersteinrichtung ist noch nicht abgeschlossen.')
        self.docker.check()
        self.docker.start(names)
