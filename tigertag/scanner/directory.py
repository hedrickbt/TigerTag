import imghdr
import logging
import os

from tigertag.scanner import Scanner
from tigertag.util import calc_hash

logger = logging.getLogger(__name__)


class DirectoryScanner(Scanner):
    def __init__(self, name, enabled):
        super().__init__(name, enabled)
        self.path = None

    def scan(self):
        if self.path is None and 'PATH' in self.props:
            self.path = self.props['PATH']
        if self.path is None:
            raise ValueError('The path has not been set for the {} ({}.{})'.format(
                self.name, __name__, type(self).__name__))
        self.path = os.path.abspath(self.path)
        for root, directories, filenames in os.walk(self.path):
            for filename in filenames:
                full_filename = os.path.normpath(os.path.join(root, filename))
                image_type = imghdr.what(full_filename)
                if image_type is None:
                    logger.debug('Ignoring {}'.format(full_filename))
                else:
                    logger.info('Scanning {}'.format(full_filename))
                    file_hash = calc_hash(full_filename)
                    file_info = {
                        'file_path': full_filename,
                        'file_hash': file_hash,
                    }
                    for listener in self.listeners:
                        listener.on_file(self, file_info)
