import unittest

from tigertag.engine.imagga import *


class TestImaggaEngine(unittest.TestCase):
    def on_tags(self, tag_info):
        self.found_tags[tag_info['file_path']] = tag_info

    def setUp(self):
        input_path = os.path.realpath(os.path.join(os.getcwd(), 'data', 'images', 'input'))
        output_path = os.path.realpath(os.path.join(os.getcwd(), 'data', 'images', 'output'))
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
        input_file_path = os.path.realpath(
            os.path.join(os.getcwd(), 'data', 'images', 'input', 'boy.jpg'))
        self.assertIn(input_file_path, self.found_tags)
        tagged_item = self.found_tags[input_file_path]
        self.assertEqual('2b87de0a02694a0448471066fe0bff79b1ab555da4d16c36560e14b18d22e42a',
                         tagged_item['file_hash'])
        # Confidence was 44.7116928100586 on 11.28.2021
        self.assertIn('portrait', tagged_item['tags'])
        self.assertGreater(50, tagged_item['tags']['portrait']['confidence'])
        self.assertLess(40, tagged_item['tags']['portrait']['confidence'])

        input_file_path = os.path.realpath(
            os.path.join(os.getcwd(), 'data', 'images', 'input', 'girl.jpg'))
        self.assertIn(input_file_path, self.found_tags)
        tagged_item = self.found_tags[input_file_path]
        self.assertEqual('d88456c386f2f4a1165728162419a230d7dc75f73198aa685a0ac03cf3ba2ab2',
                         tagged_item['file_hash'])
        # Confidence was 74.9766006469727 on 11.28.2021
        self.assertIn('afro', tagged_item['tags'])
        self.assertGreater(80, tagged_item['tags']['afro']['confidence'])
        self.assertLess(70, tagged_item['tags']['afro']['confidence'])

        input_file_path = os.path.realpath(
            os.path.join(os.getcwd(), 'data', 'images', 'input', 'puppy.jpg'))
        self.assertIn(input_file_path, self.found_tags)
        tagged_item = self.found_tags[input_file_path]
        self.assertEqual('f4d9d946c0ff1ded0ce1c5139a5a0eb8d0e514d5e4256ee5afe6d89bba68470c',
                         tagged_item['file_hash'])
        self.assertIn('dog', tagged_item['tags'])
        self.assertEqual(100, tagged_item['tags']['dog']['confidence'])

        input_file_path = os.path.realpath(os.path.join(os.getcwd(), 'data', 'images', 'input', 'sunflower.jpg'))
        self.assertIn(input_file_path, self.found_tags)
        tagged_item = self.found_tags[input_file_path]
        self.assertEqual('7bbafa42a91fba3eea845133afa79f7e665c80ffc1d8e2ca53be25120c4cfe66',
                         tagged_item['file_hash'])
        self.assertIn('sunflower', tagged_item['tags'])
        self.assertEqual(100, tagged_item['tags']['sunflower']['confidence'])


