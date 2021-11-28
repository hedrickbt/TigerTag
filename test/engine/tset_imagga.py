import unittest

from tigertag.engine.imagga import *


class TestImaggaEngine(unittest.TestCase):
    def on_tags(self, tag_info):
        self.found_tags.append(tag_info)

    def setUp(self):
        self.found_tags = []
        self.e = ImaggaEngine('imagga_engine', True)
        self.e.props['API_KEY'] = os.environ['IMAGGA_API_KEY']  # EX: acc_9...
        self.e.props['API_SECRET'] = os.environ['IMAGGA_API_SECRET']  # EX: 3e0b5...
        self.e.props['API_URL'] = os.environ['IMAGGA_API_URL']  # EX: https://api.imagga.com/v2
        self.e.props['INPUT_LOCATION'] = os.environ['IMAGGA_INPUT_LOCATION']  # EX: ../../data/images/input
        self.e.props['OUTPUT_LOCATION'] = os.environ['IMAGGA_OUTPUT_LOCATION']  # EX: ../../data/images/output
        self.e.on_tags = self.on_tags

    def test_run(self):
        self.e.run()
        print(self.found_tags)

