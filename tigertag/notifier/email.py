import logging
import os

from tigertag.notifier import Notifier
from tigertag.notifier import NotificationInfo

logger = logging.getLogger(__name__)


class EmailNotifier(Notifier):
    def __init__(self, name, enabled):
        super().__init__(name, enabled)
        self.from_address = None
        self.to = None
        self.server = None
        self.port = None
        self.start_tls = False

    def setup(self):
        if self.server is None:
            self.from_address = self.get_prop('FROM')
            if self.from_address is None and 'FROM' in self.props:
                self.from_address = self.props['PATH']
            if self.path is None:
                raise ValueError('The path has not been set for the {} ({}.{})'.format(
                    self.name, __name__, type(self).__name__))

    def notify(self, notification: NotificationInfo):
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
                    file_info = FileInfo(filename, full_filename, file_hash, None, None)
                    for listener in self.listeners:
                        listener.on_file(self, file_info)
