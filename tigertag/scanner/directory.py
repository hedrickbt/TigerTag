import imghdr
import logging
import os

from tigertag.scanner import Scanner

logger = logging.getLogger(__name__)


class DirectoryScanner(Scanner):
    def __init__(self, name, enabled, path):
        super().__init__(name, enabled)
        self.path = path

    def scan(self):
        for root, directories, filenames in os.walk(self.path):
            for filename in filenames:
                full_filename = os.path.normpath(os.path.join(root, filename))
                image_type = imghdr.what(full_filename)
                if image_type is None:
                    logger.debug('Ignoring {}'.format(full_filename))
                else:
                    logger.debug('Scanning {}'.format(full_filename))
                    for listener in self.listeners:
                        file_info = {
                            'file_path': full_filename,
                        }
                        listener.on_file(self, file_info)
