import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'compose'))
from _manager.config import Configuration, read_env
from _manager.model import ManagerError, Stack

spec = importlib.util.spec_from_file_location('gitlab_stack', ROOT / 'compose/gitlab/stack.py')
gitlab = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gitlab)


class GitLabSettings(unittest.TestCase):
    def test_choice_is_saved_and_reused_without_second_prompt(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)
            for name in ('compose.yml', '.env.example'):
                shutil.copyfile(ROOT / 'compose/gitlab' / name, path / name)
            stacks = {'gitlab': Stack('gitlab', path, 'GitLab')}
            config = Configuration(stacks, ['gitlab'])
            with patch('builtins.input', side_effect=['invalid', 'j']) as ask:
                gitlab.configure(None, config)
            self.assertEqual(ask.call_count, 2)
            config.collect(lambda *args: args[2] or 'test-value')
            config.write()
            self.assertEqual(read_env(path / '.env')['GITLAB_WEB_IDE_MARKETPLACE_FALLBACK'], 'true')
            repeated = Configuration(stacks, ['gitlab'])
            with patch('builtins.input', side_effect=AssertionError('Asked again')):
                gitlab.configure(None, repeated)
            self.assertEqual(repeated.values['gitlab.GITLAB_WEB_IDE_MARKETPLACE_FALLBACK'], 'true')

    def test_default_is_disabled(self):
        config = SimpleNamespace(values={})
        with patch('builtins.input', return_value=''):
            gitlab.configure(None, config)
        self.assertEqual(config.values['gitlab.GITLAB_WEB_IDE_MARKETPLACE_FALLBACK'], 'false')

    def test_invalid_saved_choice_is_rejected(self):
        config = SimpleNamespace(values={'gitlab.GITLAB_WEB_IDE_MARKETPLACE_FALLBACK': 'maybe'})
        with self.assertRaises(ManagerError):
            gitlab.configure(None, config)

    def test_both_choices_are_applied_and_registration_stays_disabled(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)
            context = SimpleNamespace(stacks={'gitlab': SimpleNamespace(path=path)}, docker=Mock())
            for value in ('true', 'false'):
                with self.subTest(value=value):
                    (path / '.env').write_text(f'GITLAB_WEB_IDE_MARKETPLACE_FALLBACK={value}\n')
                    gitlab.after_start(context)
                    call = context.docker.exec.call_args
                    payload = json.loads(call.kwargs['input'])
                    self.assertEqual(payload, {'signup_enabled': False,
                        'vscode_extension_marketplace_single_origin_fallback_enabled': value == 'true'})
                    self.assertEqual(call.args[:4], ('gitlab', 'gitlab', 'gitlab-rails', 'runner'))

    def test_invalid_or_missing_choice_never_calls_gitlab(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)
            context = SimpleNamespace(stacks={'gitlab': SimpleNamespace(path=path)}, docker=Mock())
            for text in ('', 'GITLAB_WEB_IDE_MARKETPLACE_FALLBACK=maybe\n'):
                (path / '.env').write_text(text)
                with self.assertRaises(ManagerError):
                    gitlab.after_start(context)
            context.docker.exec.assert_not_called()

    def test_application_error_is_not_hidden(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)
            (path / '.env').write_text('GITLAB_WEB_IDE_MARKETPLACE_FALLBACK=false\n')
            docker = Mock()
            docker.exec.side_effect = ManagerError('GitLab rejected application settings')
            with self.assertRaises(ManagerError):
                gitlab.after_start(SimpleNamespace(stacks={'gitlab': SimpleNamespace(path=path)}, docker=docker))


class ConfigurationHookLifecycle(unittest.TestCase):
    @patch('_manager.lifecycle.ensure_secret_group')
    @patch('_manager.lifecycle.Configuration')
    def test_stack_choice_is_collected_before_general_values(self, config_class, unused):
        from _manager.lifecycle import Context
        context = Context.__new__(Context)
        context.stacks = {
            'core': Stack('core', Path('.'), 'core'),
            'gitlab': Stack('gitlab', Path('.'), 'gitlab', requires=['core'], module=gitlab),
        }
        context.check_templates = Mock()
        context.docker = Mock()
        context.state = Mock()
        config = config_class.return_value
        config.values = {}
        def collect():
            self.assertEqual(config.values['gitlab.GITLAB_WEB_IDE_MARKETPLACE_FALLBACK'], 'false')
            raise EOFError('Stop before writing or starting services')
        config.collect.side_effect = collect
        with patch('builtins.input', return_value='') as ask, self.assertRaises(EOFError):
            context.initialize(['gitlab'])
        ask.assert_called_once()
        config.write.assert_not_called()
        context.docker.start.assert_not_called()
