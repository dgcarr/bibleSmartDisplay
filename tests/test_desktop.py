import json
import logging
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from datetime import datetime
from filelock import FileLock, Timeout
from desktop import core, scheduler
from desktop.i18n import CATALOG, ROWS, LANGUAGES


class DesktopTests(unittest.TestCase):
    def tearDown(self):
        for handler in logging.getLogger().handlers[:]:
            handler.close()
            logging.getLogger().removeHandler(handler)

    def test_settings_validation_and_roundtrip(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.assertEqual(core.load(root)['color'], '#ADD8E6')
            for language in LANGUAGES:
                core.save(root, dict(core.DEFAULTS, language=language, color='#112233'))
                self.assertEqual(core.load(root)['language'], language)
            for changes in ({'version': 2}, {'model': 'wrong'}, {'brightness': 101}, {'time': '25:99'}, {'color': 'bad color'}, {'scheduled': 'yes'}, {'language': 'bad'}):
                with self.assertRaises((ValueError, TypeError)):
                    core.save(root, dict(core.DEFAULTS, **changes))
            self.assertFalse((root / 'settings.json.tmp').exists())

    def test_identity_reconnection_and_ambiguity(self):
        first = SimpleNamespace(device='COM3', vid=1, pid=2, serial_number='unique')
        second = SimpleNamespace(device='COM9', vid=1, pid=2, serial_number='unique')
        data = dict(core.DEFAULTS, port='COM3', identity=core.identity(first))
        self.assertEqual(core.resolve(data, [second]), 'COM9')
        for ports in ([], [first, second]):
            with self.assertRaises(ValueError):
                core.resolve(data, ports)
        self.assertEqual(core.resolve(dict(data, identity=None), [first]), 'COM3')

    def test_due_and_catch_up(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            data = dict(core.DEFAULTS, scheduled=True)
            self.assertFalse(core.due(root, data, datetime(2026, 1, 1, 5, 59)))
            self.assertTrue(core.due(root, data, datetime(2026, 1, 1, 12)))
            (root / 'last-scheduled.json').write_text('{"date":"2026-01-01"}')
            self.assertFalse(core.due(root, data, datetime(2026, 1, 1, 12)))
            self.assertTrue(core.due(root, data, datetime(2026, 1, 2, 6)))

    def test_retry_and_scheduler_lock(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            core.save(root, dict(core.DEFAULTS, scheduled=True, time='00:00'))
            with patch('subprocess.run', return_value=SimpleNamespace(returncode=0, stdout='active')), patch.object(core, 'run', side_effect=[OSError('unplugged'), None]) as run, patch.object(core.time, 'sleep') as sleep:
                core.scheduled(root)
                self.assertEqual(run.call_count, 2)
                self.assertTrue((root / 'last-scheduled.json').exists())
                self.assertEqual(sleep.call_args.args, (30,))
            with patch('subprocess.run', return_value=SimpleNamespace(returncode=0, stdout='active')), FileLock(str(root / 'scheduler.lock')):
                with self.assertRaises(Timeout):
                    core.scheduled(root)

    def test_engine_lock_rejects_concurrent_update(self):
        with tempfile.TemporaryDirectory() as temp:
            with FileLock(str(Path(temp) / '.lock')):
                with self.assertRaises(RuntimeError):
                    core.run(Path(temp), dict(core.DEFAULTS), 'preview')

    def test_preview_offline_and_no_usb(self):
        with tempfile.TemporaryDirectory() as temp:
            with patch.object(core, 'resolve', side_effect=AssertionError('USB')), patch.object(core.engine, 'fetch', side_effect=AssertionError('network')):
                core.run(Path(temp), dict(core.DEFAULTS), 'preview')
            self.assertTrue((Path(temp) / 'preview.png').exists())

    def test_catalogue_complete(self):
        self.assertEqual(len(ROWS), len(CATALOG['en']))
        for language in LANGUAGES:
            self.assertEqual(set(CATALOG[language]), set(CATALOG['en']))
            self.assertTrue(all(CATALOG[language].values()))

    def test_linux_registration_and_removal(self):
        with tempfile.TemporaryDirectory(prefix='Bible space ') as temp:
            home = Path(temp)
            with patch.object(scheduler.sys, 'platform', 'linux'), patch.object(scheduler.Path, 'home', return_value=home), patch.object(scheduler, 'call') as call, patch.object(scheduler.subprocess, 'run'):
                data = dict(core.DEFAULTS, scheduled=True, startup=True)
                scheduler.configure(home, data)
                service = home / '.config/systemd/user/biblesmartdisplay.service'
                self.assertIn('--scheduled', service.read_text())
                self.assertIn('Bible space', service.read_text())
                self.assertTrue((home / '.config/autostart/biblesmartdisplay.desktop').exists())
                scheduler.configure(home, dict(data, scheduled=False, startup=False))
                self.assertFalse(service.exists())
                self.assertFalse((home / '.config/autostart/biblesmartdisplay.desktop').exists())

    def test_windows_xml(self):
        import xml.etree.ElementTree as ET
        with tempfile.TemporaryDirectory() as temp:
            with patch.object(scheduler.sys, 'platform', 'win32'), patch.object(scheduler.subprocess, 'check_output', return_value='PC\\User'), patch.object(scheduler, 'call'):
                scheduler.configure(Path(temp), dict(core.DEFAULTS, scheduled=True, startup=True))
            xml = ET.fromstring((Path(temp) / 'Daily.xml').read_text('utf-16'))
            ns = {'t': 'http://schemas.microsoft.com/windows/2004/02/mit/task'}
            self.assertEqual(xml.find('.//t:LogonType', ns).text, 'InteractiveToken')
            self.assertIn('--scheduled', xml.find('.//t:Arguments', ns).text)

    @unittest.skipIf(os.name == 'nt', 'POSIX launchd uid')
    def test_macos_plist(self):
        import plistlib
        with tempfile.TemporaryDirectory() as temp:
            with patch.object(scheduler.sys, 'platform', 'darwin'), patch.object(scheduler.Path, 'home', return_value=Path(temp)), patch.object(scheduler, 'call'), patch.object(scheduler.subprocess, 'run'):
                scheduler.configure(Path(temp), dict(core.DEFAULTS, scheduled=True, startup=True))
                path = Path(temp) / 'Library/LaunchAgents/org.biblesmartdisplay.daily.plist'
                self.assertIn('--scheduled', plistlib.loads(path.read_bytes())['ProgramArguments'])
                scheduler.configure(Path(temp), dict(core.DEFAULTS))
                self.assertFalse(path.exists())


try:
    from PySide6.QtWidgets import QApplication, QSystemTrayIcon
    from desktop.gui import Window, SetupWizard
    QT = True
except ImportError:
    import importlib.util
    if importlib.util.find_spec('PySide6') is not None:
        raise
    QT = False


@unittest.skipUnless(QT, 'Desktop dependencies not installed')
class GuiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
        cls.app = QApplication.instance() or QApplication([])

    def test_settings_in_every_language_and_no_tray(self):
        for language in LANGUAGES:
            with self.subTest(language=language), tempfile.TemporaryDirectory() as temp:
                core.save(Path(temp), dict(core.DEFAULTS, language=language))
                window = Window(Path(temp))
                self.assertEqual(window.settings.values()['language'], language)
                with patch.object(QSystemTrayIcon, 'isSystemTrayAvailable', return_value=False):
                    window.show()
                    window.close()
                    self.assertFalse(window.isVisible())
                window.timer.stop()
                window.tray.hide()
                window.deleteLater()
                self.app.processEvents()

    def test_wizard_has_real_controls_and_requires_test(self):
        with tempfile.TemporaryDirectory() as temp:
            window = Window(Path(temp))
            wizard = SetupWizard(window)
            self.assertEqual(len(wizard.pageIds()), 4)
            self.assertFalse(wizard.page(2).isComplete())
            self.assertIs(window.settings.model.parent(), wizard.page(0))
            wizard.reject()
            self.assertEqual(window.settings.values()['color'], '#ADD8E6')
            window.timer.stop()
            window.tray.hide()
            window.deleteLater()
            self.app.processEvents()


@unittest.skipUnless(QT, 'Desktop dependencies not installed')
class InstallerTests(unittest.TestCase):
    def test_per_user_install_with_spaces(self):
        from desktop import install
        from PySide6.QtWidgets import QMessageBox
        app = QApplication.instance() or QApplication([])
        with tempfile.TemporaryDirectory(prefix='Bible installer ') as temp:
            base = Path(temp)
            source = base / 'download'
            source.mkdir()
            (source / 'BibleSmartDisplay').write_bytes(b'test executable')
            (source / '_internal').mkdir()
            (source / '_internal/runtime').write_bytes(b'test runtime')
            home = base / 'user home'
            with patch.object(install.Path, 'home', return_value=home), patch.object(install.sys, 'executable', str(source / 'BibleSmartDisplay')), patch.object(QMessageBox, 'question', return_value=QMessageBox.StandardButton.Yes), patch.object(QMessageBox, 'information'), patch.object(install.subprocess, 'Popen') as launch:
                self.assertEqual(install.install(), 0)
                target = home / '.local/opt/bibleSmartDisplay'
                self.assertEqual((target / '_internal/runtime').read_bytes(), b'test runtime')
                self.assertEqual(launch.call_args.args[0], [str(target / 'BibleSmartDisplay')])
                self.assertIn('user home', (home / '.local/share/applications/biblesmartdisplay.desktop').read_text())
