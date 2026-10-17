import importlib.util
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('display', Path(__file__).parents[1] / 'outputs/daily-verse/verse_display.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class DisplayTests(unittest.TestCase):
    def test_preview_without_network_or_serial(self):
        with tempfile.TemporaryDirectory() as temp:
            with patch.object(m.sys, 'argv', ['display', '--demo', '--preview-only', '--data-dir', temp]), patch.object(m, 'fetch', side_effect=AssertionError('Network accessed')), patch.object(m, 'display', side_effect=AssertionError('Serial accessed')):
                m.main()
            with m.Image.open(Path(temp) / 'preview.png') as im:
                self.assertEqual(im.size, (480, 320))
                self.assertIn((173, 216, 230), im.getdata())
            self.assertFalse((Path(temp) / 'last-verse.json').exists())
            # Release log file handles for Windows temporary-directory cleanup.
            for handler in m.logging.getLogger().handlers[:]:
                handler.close()
                m.logging.getLogger().removeHandler(handler)

    def test_ambiguous_auto_detection_refuses(self):
        from types import SimpleNamespace
        ports = [SimpleNamespace(device=p, serial_number='USB35INCHIPSV2') for p in ['COM3', 'COM4']]
        with patch.object(m.list_ports, 'comports', return_value=ports):
            with self.assertRaises(ValueError):
                m.choose_port()
        with patch.object(m.list_ports, 'comports', return_value=ports[:1]):
            self.assertEqual(m.choose_port(), 'COM3')

    def test_windows_serial_and_frame(self):
        with patch.object(m.os, 'name', 'nt'), patch.object(m.serial, 'Serial') as factory, patch.object(m.time, 'sleep'):
            port = factory.return_value.__enter__.return_value
            port.read.return_value = bytes([1]) * 6
            m.display(m.Image.new('RGB', (480, 320), 'black'), 'COM3', 50)
            self.assertNotIn('exclusive', factory.call_args.kwargs)
            writes = [c.args[0] for c in port.write.call_args_list]
            self.assertEqual(writes[2], m.command(110, x=128))
            self.assertEqual(sum(map(len, writes[5:])), 480 * 320 * 2)

    def test_wrong_handshake_does_not_send_frame(self):
        with patch.object(m.serial, 'Serial') as factory:
            port = factory.return_value.__enter__.return_value
            port.read.return_value = b'wrong!'
            with self.assertRaises(RuntimeError):
                m.display(m.Image.new('RGB', (480, 320)), 'COM3')
            self.assertEqual(port.write.call_count, 1)


if __name__ == '__main__':
    unittest.main()
