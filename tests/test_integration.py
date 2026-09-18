import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import yaml
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'compose'))
from _manager.config import Configuration, read_env
from _manager.model import Stack, ManagerError
from _manager.backup import Mount, export_archive, import_archive, inspect_archive
from _manager.lifecycle import Context

class SharedConfiguration(unittest.TestCase):
    def test_one_prompt_two_destinations_and_repeated_setup(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)
            (path/'compose.yml').write_text('secrets:\n  password:\n    file: ./secrets/password\n')
            (path/'.env.example').write_text('PW=!<KEY | generate="openssl rand -hex 32">\nFILE=-<KEY | targets=password>\n')
            stacks={'db':Stack('db',path,'db')}
            calls=[]
            config=Configuration(stacks,['db'])
            config.collect(lambda *args: calls.append(args) or 'a$#=\'secret')
            config.write()
            self.assertEqual(len(calls),1)
            self.assertTrue(calls[0][1])
            self.assertEqual(read_env(path/'.env')['PW'],(path/'secrets/password').read_text())
            repeated=Configuration(stacks,['db'])
            repeated.collect(lambda *args: self.fail('Erneute Abfrage'))
            (path/'secrets/password').write_text('different')
            with self.assertRaises(ManagerError):Configuration(stacks,['db'])

    def test_all_repository_templates(self):
        context=Context(Path(__file__).resolve().parents[1]/'compose')
        context.check_templates()
        self.assertEqual(len(context.stacks),19)
        for stack in context.stacks.values():
            if stack.name!='core':self.assertIn('core',stack.requires)

class RoundTrip(unittest.TestCase):
    @patch('_manager.backup.users_of_mounts', return_value=[])
    def test_directory_file_and_relative_symlink(self, unused):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder);source=p/'source';source.mkdir()
            (source/'file').write_bytes(b'\x00payload\xff')
            (source/'link').symlink_to('file')
            extra=p/'extra';extra.write_text('config')
            archive=p/'snapshot.tar.gz'
            export_archive(archive,'example','app',[Mount(str(source),'/data','bind'),Mount(str(extra),'/config','bind')])
            self.assertEqual(len(inspect_archive(archive)['mounts']),2)
            dest=p/'dest';dest.mkdir();(dest/'old').write_text('remove')
            output=p/'output'
            import_archive(archive,{0:dest,1:output},replace=True)
            self.assertEqual((dest/'file').read_bytes(),b'\x00payload\xff')
            self.assertEqual((dest/'link').readlink(),Path('file'))
            self.assertFalse((dest/'old').exists())
            self.assertEqual(output.read_text(),'config')

    @patch('_manager.backup.users_of_mounts', return_value=[])
    def test_configuration_requires_encryption(self,unused):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder); source=p/'source';source.mkdir()
            with self.assertRaises(ManagerError):
                export_archive(p/'out.tar.gz','x','x',[Mount(str(source),'/data','bind')],config=p)

class BackupFailure(unittest.TestCase):
    @patch('_manager.backup.run')
    @patch('_manager.backup.users_of_mounts', return_value=['container'])
    def test_failed_restore_does_not_restart_containers(self, users, run):
        from _manager.backup import quiesce
        with self.assertRaises(RuntimeError):
            with quiesce([], restart_on_error=False):
                raise RuntimeError('restore failed')
        self.assertEqual([c.args[0][1] for c in run.call_args_list], ['stop'])

    def test_failed_scheduled_backup_preserves_previous_archive(self):
        from types import SimpleNamespace
        from _manager.scheduler import tick
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder); path=root/'_backup'/'s'/'v';path.mkdir(parents=True)
            (path/'old.tar.gz').write_text('existing backup')
            job={'id':'abc','stack':'s','service':'v','targets':['/data'],'cron':'0 3 * * *',
                 'timezone':'UTC','keep':1,'next':'2020-01-01T00:00:00+00:00','archives':['old.tar.gz']}
            context=SimpleNamespace(root=root,state=SimpleNamespace(data={'backups':[job]},save=lambda:None),docker=None)
            with patch('_manager.scheduler.inventory', return_value=[Mount('/fake','/data','bind')]), patch('_manager.scheduler.export_archive', side_effect=ManagerError('failure')):
                with self.assertRaises(ManagerError):tick(context)
            self.assertTrue((path/'old.tar.gz').exists())
            self.assertEqual(job['archives'],['old.tar.gz'])
            self.assertIn('error',job)
