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
