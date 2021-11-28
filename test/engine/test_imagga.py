import unittest

from tigertag.engine.imagga import *


class TestImaggaEngine(unittest.TestCase):
    def on_tags(self, tag_info):
        self.found_tags[tag_info['file_path']] = tag_info

    def setUp(self):
        input_path = os.path.realpath(os.path.join(os.getcwd(), '..', 'data', 'images', 'input'))
        output_path = os.path.realpath(os.path.join(os.getcwd(), '..', 'data', 'images', 'output'))
        self.found_tags = {}
        self.e = ImaggaEngine('imagga_engine', True)
        self.e.props['API_KEY'] = os.environ['IMAGGA_API_KEY']  # EX: acc_9...
        self.e.props['API_SECRET'] = os.environ['IMAGGA_API_SECRET']  # EX: 3e0b5...
        self.e.props['API_URL'] = 'https://api.imagga.com/v2'
        self.e.props['INPUT_LOCATION'] = input_path
        self.e.props['OUTPUT_LOCATION'] = output_path
        self.e.on_tags = self.on_tags

    def test_run(self):
        self.e.run()
        input_file_path = os.path.realpath(os.path.join(os.getcwd(), '..', 'data', 'images', 'input', 'DSC_0083_1.JPG'))
        self.assertIn(input_file_path, self.found_tags)
        tagged_item = self.found_tags[input_file_path]

        self.assertEqual('30ee14cf3184a64248fec8abcc0170f7578686978ff8f401c80016ac10ec797c',
                         tagged_item['file_hash'])

        self.assertIn('herb', tagged_item['tags'])
        self.assertEqual(100, tagged_item['tags']['herb']['confidence'])

        # Confidence was 80.4872 on 11.28.2021
        self.assertIn('plant', tagged_item['tags'])
        self.assertGreater(85, tagged_item['tags']['plant']['confidence'])
        self.assertLess(75, tagged_item['tags']['plant']['confidence'])


