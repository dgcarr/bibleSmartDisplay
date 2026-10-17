"""Rendering contract across supported display sizes."""
import unittest
from desktop.core import engine


class RenderingTests(unittest.TestCase):
    def test_all_model_resolutions_keep_rgb_and_black_margins(self):
        for dimensions in sorted({model[:2] for model in engine.MODELS.values()}):
            with self.subTest(size=dimensions):
                image = engine.render({'verse': 'Be sober-minded, be alert.', 'reference': '1 Peter 5:8 CSB'}, color='#ADD8E6', size=dimensions)
                self.assertEqual(image.size, dimensions)
                self.assertEqual(image.mode, 'RGB')
                bbox = image.getbbox()
                self.assertIsNotNone(bbox)
                self.assertGreater(bbox[0], 0)
                self.assertGreater(bbox[1], 0)
                self.assertLess(bbox[2], dimensions[0])
                self.assertLess(bbox[3], dimensions[1])
                # Preserve black background and blue text, including blended edges.
                colors = {pixel for _, pixel in image.getcolors(image.width * image.height)}
                self.assertIn((0, 0, 0), colors)
                self.assertIn((173, 216, 230), colors)
                self.assertGreater(len(colors), 10)

    def test_long_verse_fits_or_fails_explicitly(self):
        data = {'verse': 'Be sober-minded, be alert. Your adversary the devil is prowling around like a roaring lion, looking for anyone he can devour.', 'reference': '1 Peter 5:8 CSB'}
        image = engine.render(data)
        self.assertEqual(image.size, (480, 320))
        self.assertLess(image.getbbox()[3], 320)
        with self.assertRaisesRegex(ValueError, 'cannot fit'):
            engine.render(dict(data, verse='word ' * 2000))
