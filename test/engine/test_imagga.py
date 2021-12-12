import unittest

from tigertag.engine.imagga import *


class TestImaggaEngine(unittest.TestCase):
    def on_tags(self, engine: Engine, tag_info: TagInfo):
        self.found_tags[tag_info.path] = tag_info

    def setUp(self):
        self.found_tags: dict[str, TagInfo] = {}
        self.e = ImaggaEngine('imagga_engine', True)
        self.e.props['API_KEY'] = os.environ['IMAGGA_API_KEY']  # EX: acc_9...
        self.e.props['API_SECRET'] = os.environ['IMAGGA_API_SECRET']  # EX: 3e0b5...
        self.e.props['API_URL'] = 'https://api.imagga.com/v2'
        el = EngineListener()
        el.on_tags = self.on_tags
        self.e.listeners.append(el)

    def test_tag_boy(self):
        input_file_path = os.path.normpath(
            os.path.join(os.getcwd(), 'data', 'images', 'input', 'boy.jpg'))
        self.e.tag(input_file_path)
        self.assertIn(input_file_path, self.found_tags)
        tagged_item = self.found_tags[input_file_path]
        # Confidence was 44.7116928100586 on 11.28.2021
        tag_name = self.e.calc_tag_name('portrait')
        self.assertIn(tag_name, tagged_item.tags)
        self.assertGreater(50, tagged_item.tags[tag_name]['confidence'])
        self.assertLess(40, tagged_item.tags[tag_name]['confidence'])

    def test_tag_girl(self):
        input_file_path = os.path.normpath(
            os.path.join(os.getcwd(), 'data', 'images', 'input', 'girl.jpg'))
        self.e.tag(input_file_path)
        self.assertIn(input_file_path, self.found_tags)
        tagged_item = self.found_tags[input_file_path]
        # Confidence was 74.9766006469727 on 11.28.2021
        tag_name = self.e.calc_tag_name('afro')
        self.assertIn(tag_name, tagged_item.tags)
        self.assertGreater(80, tagged_item.tags[tag_name]['confidence'])
        self.assertLess(70, tagged_item.tags[tag_name]['confidence'])

    def test_tag_puppy(self):
        input_file_path = os.path.normpath(
            os.path.join(os.getcwd(), 'data', 'images', 'input', 'puppy.jpg'))
        self.e.tag(input_file_path)
        self.assertIn(input_file_path, self.found_tags)
        tagged_item = self.found_tags[input_file_path]
        tag_name = self.e.calc_tag_name('dog')
        self.assertIn(tag_name, tagged_item.tags)
        self.assertEqual(100, tagged_item.tags[tag_name]['confidence'])

    def test_tag_sunflower(self):
        input_file_path = os.path.normpath(os.path.join(os.getcwd(), 'data', 'images', 'input', 'sunflower.jpg'))
        self.e.tag(input_file_path)
        self.assertIn(input_file_path, self.found_tags)
        tagged_item = self.found_tags[input_file_path]
        tag_name = self.e.calc_tag_name('sunflower')
        self.assertIn(tag_name, tagged_item.tags)
        self.assertEqual(100, tagged_item.tags[tag_name]['confidence'])
