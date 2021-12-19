import sys
import unittest

from tigertag.engine.compreface import *
from tigertag.engine import EngineListener

logging.basicConfig(
    stream=sys.stderr,
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)-8s %(name)s : %(funcName)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')


class TestComprefaceEngine(unittest.TestCase):
    def on_tags(self, engine: Engine, tag_info: TagInfo, ext_id: str):
        self.found_tags[tag_info.path] = tag_info

    def setUp(self):
        self.found_tags: dict[str, TagInfo] = {}
        self.e = ComprefaceEngine('compreface_engine', 'ttf', True)
        self.e.props['FACES_FOLDER'] = os.path.normpath(os.path.join(
            os.getcwd(), 'data', 'images', 'faces'))
        self.e.props['FACES_CONFIG'] = os.path.normpath(os.path.join(
            os.getcwd(), 'data', 'images', 'faces', 'faces.yaml'))
        self.e.props['API_KEY'] = os.environ['COMPREFACE_API_KEY']  # EX: 5b3448dc-f...
        self.e.props['API_URL'] = 'http://localhost'
        self.e.props['API_PORT'] = '8000'
        el = EngineListener()
        el.on_tags = self.on_tags
        self.e.listeners.append(el)

    def test_upload_faces(self):
        self.e.delete_all_faces()

        result = self.e.upload_faces()
        subjects = result['subjects']
        self.assertEqual(2, len(subjects))
        self.assertIn('Roman', subjects)
        self.assertIn('Poppy', subjects)

        upload_count = result['uploaded']
        self.assertEqual(3, upload_count)

    def test_tag_boy(self):
        input_file_path = os.path.normpath(
            os.path.join(os.getcwd(), 'data', 'images', 'input', 'boy.jpg'))
        self.e.tag(input_file_path)
        self.assertIn(input_file_path, self.found_tags)
        tagged_item = self.found_tags[input_file_path]
        tag_name = self.e.calc_tag_name('Roman')
        self.assertIn(tag_name, tagged_item.tags)
        self.assertEqual(100, tagged_item.tags[tag_name]['confidence'])

    def test_tag_boy2(self):
        input_file_path = os.path.normpath(
            os.path.join(os.getcwd(), 'data', 'images', 'input', 'boy2.jpg'))
        self.e.tag(input_file_path)
        self.assertIn(input_file_path, self.found_tags)
        tagged_item = self.found_tags[input_file_path]
        tag_name = self.e.calc_tag_name('Roman')
        self.assertIn(tag_name, tagged_item.tags)
        self.assertGreater(101, tagged_item.tags[tag_name]['confidence'])
        self.assertLess(90, tagged_item.tags[tag_name]['confidence'])

    def test_tag_girl(self):
        input_file_path = os.path.normpath(
            os.path.join(os.getcwd(), 'data', 'images', 'input', 'girl.jpg'))
        self.e.tag(input_file_path)
        self.assertIn(input_file_path, self.found_tags)
        tagged_item = self.found_tags[input_file_path]
        tag_name = self.e.calc_tag_name('Poppy')
        self.assertIn(tag_name, tagged_item.tags)
        self.assertGreater(101, tagged_item.tags[tag_name]['confidence'])
        self.assertLess(90, tagged_item.tags[tag_name]['confidence'])

    def test_tag_puppy_no_tags(self):
        input_file_path = os.path.normpath(
            os.path.join(os.getcwd(), 'data', 'images', 'input', 'puppy.jpg'))
        self.e.tag(input_file_path)
        self.assertIn(input_file_path, self.found_tags)
        tagged_item = self.found_tags[input_file_path]
        self.assertEqual(0, len(tagged_item.tags))
