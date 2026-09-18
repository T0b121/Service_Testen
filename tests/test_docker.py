import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'compose'))
from _manager.docker import validate_exposure
from _manager.model import ManagerError

class Exposure(unittest.TestCase):
    def test_api_must_be_protected(self):
        data = {'services': {'app': {'labels': {'traefik.http.routers.api.rule': 'Host(`x`)'}}}}
        with self.assertRaises(ManagerError):
            validate_exposure('test', data)
        data['services']['app']['labels']['traefik.http.routers.api.middlewares'] = 'authentik@docker'
        validate_exposure('test', data)
        data['services']['app']['ports'] = ['8080:80']
        with self.assertRaises(ManagerError):
            validate_exposure('test', data)
