from test_display import m
from unittest.mock import patch, MagicMock
import unittest

class ModelTests(unittest.TestCase):
    def test_original_turing_silence_is_explicit_only(self):
        for model, succeeds in [('turing-3.5', True), ('usbpcmonitor-3.5', False)]:
            with self.subTest(model=model), patch.object(m.serial, 'Serial') as factory, patch.object(m.time, 'sleep'):
                port=factory.return_value.__enter__.return_value
                port.read.return_value=b''
                image=m.Image.new('RGB',(480,320))
                if succeeds:
                    m.display(image,'COM3',model=model)
                    self.assertGreater(port.write.call_count,5)
                else:
                    with self.assertRaises(RuntimeError):m.display(image,'COM3',model=model)
                    self.assertEqual(port.write.call_count,1)

    def test_a_sizes_and_mismatched_reply(self):
        for model, byte in [('usbpcmonitor-3.5',1),('usbpcmonitor-5',2),('usbpcmonitor-7',3)]:
            with self.subTest(model=model), patch.object(m.serial,'Serial') as factory, patch.object(m.time,'sleep'):
                size=m.MODELS[model][:2]
                image=m.render({'verse':'Display model preview.', 'reference':'Test'},size=size)
                self.assertEqual(image.size,size)
                port=factory.return_value.__enter__.return_value
                port.read.return_value=bytes([byte])*6
                m.display(image,'COM3',model=model)
                writes=[c.args[0] for c in port.write.call_args_list]
                self.assertEqual(sum(map(len,writes[5:])),size[0]*size[1]*2)
                port.reset_mock();port.read.return_value=b'bad!!!'
                with self.assertRaises(RuntimeError):m.display(image,'COM3',model=model)
                self.assertEqual(port.write.call_count,1)

    def test_b_d_actual_serializers(self):
        for model in ['xuanfang-3.5','qiye-3.5']:
            with self.subTest(model=model), patch('smartscreen_driver.lcd_comm.serial.Serial') as factory:
                port=factory.return_value
                port.write.side_effect=lambda data:len(data)
                port.read.return_value=b'\xcaHELLO\x0a\x12\x00\xca'
                m.display(m.Image.new('RGB',(480,320)),'COM3',model=model)
                self.assertGreater(sum(len(c.args[0]) for c in port.write.call_args_list),480*320*2)
                port.flush.assert_called_once()
                self.assertTrue(port.close.called)

    def test_b_bad_handshake_and_d_write_failure(self):
        for model in ['xuanfang-3.5','qiye-3.5']:
            with patch('smartscreen_driver.lcd_comm.serial.Serial') as factory:
                port=factory.return_value
                port.write.side_effect=lambda data:len(data)
                port.read.return_value=b'bad'
                if model=='qiye-3.5':port.write.side_effect=m.serial.SerialTimeoutException('test')
                with self.assertRaises((RuntimeError,m.serial.SerialTimeoutException)):
                    m.display(m.Image.new('RGB',(480,320)),'COM3',model=model)
                self.assertTrue(port.close.called)
