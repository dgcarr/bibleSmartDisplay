import os
import unittest
from unittest.mock import patch
from desktop.system import host_environment


class HostEnvironmentTests(unittest.TestCase):
    def test_frozen_removes_bundle_library_path(self):
        with patch('sys.frozen', True, create=True), patch.dict(os.environ, {'LD_LIBRARY_PATH': '/bundle', 'PATH': '/usr/bin'}, clear=True):
            self.assertNotIn('LD_LIBRARY_PATH', host_environment())
            self.assertEqual(host_environment()['PATH'], '/usr/bin')
            self.assertEqual(os.environ['LD_LIBRARY_PATH'], '/bundle')

    def test_frozen_restores_original(self):
        with patch('sys.frozen', True, create=True), patch.dict(os.environ, {'LD_LIBRARY_PATH': '/bundle', 'LD_LIBRARY_PATH_ORIG': '/host'}, clear=True):
            self.assertEqual(host_environment()['LD_LIBRARY_PATH'], '/host')

    def test_source_preserves_environment(self):
        with patch('sys.frozen', False, create=True), patch.dict(os.environ, {'LD_LIBRARY_PATH': '/host'}, clear=True):
            self.assertEqual(host_environment()['LD_LIBRARY_PATH'], '/host')
