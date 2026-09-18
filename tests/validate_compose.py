"""No containers or real credentials: validate all rendered stack files with Compose."""
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tempfile
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'compose'))
from _manager.model import discover
from _manager.config import Configuration


def main():
    command = shlex.split(os.environ.get('COMPOSE_COMMAND', 'docker compose'))
    with tempfile.TemporaryDirectory() as folder:
        target = Path(folder) / 'compose'
        shutil.copytree(ROOT / 'compose', target, ignore=shutil.ignore_patterns(
            '_state', '_backup', '_cache', '__pycache__', '.env', 'secrets'))
        stacks = discover(target)
        config = Configuration(stacks, list(stacks))
        def ask(key, secret, default, hint):
            if key == 'global.DOMAIN': return 'example.org'
            if default is not None: return default
            if 'EMAIL' in key or 'MAIL' in key: return 'admin@example.org'
            if 'VERSION' in key: return '1.0.0'
            return 'a' * 32
        config.collect(ask)
        config.write()
        for name, stack in stacks.items():
            for spec in yaml.safe_load((stack.path / 'compose.yml').read_text()).get('secrets', {}).values():
                path = stack.path / spec['file']
                path.parent.mkdir(exist_ok=True)
                path.touch(exist_ok=True)
            result = subprocess.run([*command, '--project-directory', str(stack.path),
                '--env-file', str(stack.path / '.env'), '-p', name, '-f', str(stack.path / 'compose.yml'),
                'config', '--format', 'json'], check=True, capture_output=True, text=True)
            data = json.loads(result.stdout)
            print(f'{name}: OK ({len(data["services"])} services)')


if __name__ == '__main__':
    main()
