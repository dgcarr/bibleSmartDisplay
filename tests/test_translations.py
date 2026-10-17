from test_display import m
from unittest.mock import patch
import unittest
import tempfile
import json
from pathlib import Path

class TranslationTests(unittest.TestCase):
    def test_non_english_and_annotations(self):
        parser = m.PassageParser('RVR1960')
        parser.feed('<div class="version-NIV"><span class="text" id="en-NIV-1">Wrong</span></div><div class="version-RVR1960"><span class="text" id="es-RVR1960-1">Texto <sup>1</sup>con <span>amor</span>.</span><span class="text"> Más texto.</span></div>')
        self.assertEqual(' '.join(''.join(parser.parts).split()), 'Texto con amor. Más texto.')
        self.assertEqual(len(parser.verse_ids), 1)

    def test_wrong_version_response_rejected(self):
        with patch.object(m, 'parse_page', return_value={'reference':'John 3:16 ESV'}), patch.object(m, 'download', return_value='<div class="version-NIV"><span class="text" id="en-NIV-1">Wrong translation text.</span></div>'):
            with self.assertRaises(ValueError): m.fetch('KJV')

    def test_version_validation(self):
        self.assertEqual(m.version_code(' niv '), 'NIV')
        self.assertEqual(m.version_code('erv-ar'), 'ERV-AR')
        for value in ['NIV;KJV','../NIV','', 'NIV&x=y']:
            with self.assertRaises(m.argparse.ArgumentTypeError): m.version_code(value)

    def test_failed_switch_does_not_display_old_translation(self):
        with tempfile.TemporaryDirectory() as temp:
            cache=Path(temp)/'last-verse.json'
            before=json.dumps({'verse':'Saved CSB text', 'reference':'John 3:16 CSB', 'translation':'CSB'})
            cache.write_text(before)
            try:
                with patch.object(m.sys,'argv',['app','--translation','NIV','--preview-only','--data-dir',temp]), patch.object(m,'fetch',side_effect=ValueError('unavailable')), patch.object(m,'render') as render:
                    with self.assertRaisesRegex(ValueError,'not NIV'):m.main()
                    render.assert_not_called()
                    self.assertEqual(cache.read_text(),before)
            finally:
                for h in m.logging.getLogger().handlers[:]:
                    h.close();m.logging.getLogger().removeHandler(h)
