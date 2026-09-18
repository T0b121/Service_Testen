from dataclasses import dataclass, field
from pathlib import Path
import importlib.util
import re


class ManagerError(Exception):
    """Eine verständliche, ohne Secret-Inhalte auszugebende Fehlermeldung."""


@dataclass
class Stack:
    name: str
    path: Path
    title: str
    requires: list[str] = field(default_factory=list)
    groups: list[str] = field(default_factory=list)
    applications: list[dict] = field(default_factory=list)
    module: object = None


def discover(root: Path) -> dict[str, Stack]:
    result = {}
    for path in sorted(root.iterdir()):
        if not path.is_dir() or path.name.startswith(('_', '.')):
            continue
        if not re.fullmatch(r'[a-z0-9][a-z0-9-]*', path.name):
            raise ManagerError(f'Ungültiger Stack-Name: {path.name}')
        missing = [n for n in ('stack.py', 'compose.yml', '.env.example') if not (path / n).is_file()]
        if missing:
            raise ManagerError(f'{path.name}: fehlende Dateien: {", ".join(missing)}')
        spec = importlib.util.spec_from_file_location(f'stack_{path.name}', path / 'stack.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        requires = list(getattr(module, 'REQUIRES', []))
        if path.name != 'core' and 'core' not in requires:
            requires.insert(0, 'core')
        groups = list(getattr(module, 'AUTH_GROUPS', []))
        if len(groups) != len(set(groups)) or not all(isinstance(g, str) and g for g in groups):
            raise ManagerError(f'{path.name}: ungültige AUTH_GROUPS')
        apps = list(getattr(module, 'APPLICATIONS', []))
        for app in apps:
            if not app.get('groups') or not set(app['groups']) <= set(groups):
                raise ManagerError(f'{path.name}: Anwendung benötigt deklarierte Zugriffsgruppen')
        result[path.name] = Stack(path.name, path, getattr(module, 'TITLE', path.name), requires, groups, apps, module)
    if 'core' not in result:
        raise ManagerError('Der Pflicht-Stack core fehlt.')
    order(result, list(result))  # Auch ungewählte, defekte Abhängigkeiten früh erkennen.
    return result


def order(stacks: dict[str, Stack], selected: list[str]) -> list[str]:
    result, visiting = [], []
    def visit(name):
        if name not in stacks:
            raise ManagerError(f'Unbekannte Abhängigkeit: {name}')
        if name in visiting:
            raise ManagerError('Kreisabhängigkeit: ' + ' → '.join(visiting + [name]))
        if name in result:
            return
        visiting.append(name)
        for dep in stacks[name].requires:
            visit(dep)
        visiting.pop()
        result.append(name)
    for name in ['core', *selected]:
        visit(name)
    return result
