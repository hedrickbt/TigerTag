import imghdr
import logging
import os
import tempfile

from plexapi.server import PlexServer

from tigertag.scanner import FileInfo
from tigertag.scanner import Scanner
from tigertag.util import calc_hash

logger = logging.getLogger(__name__)
DEFAULT_URL = 'http://127.0.0.1:32400'

class PlexScanner(Scanner):
    def connect(self):
        if 'TOKEN' in self.props:
            if 'URL' in self.props:
                self.url = self.props['URL']
            self.plex = PlexServer(self.url, self.props['TOKEN'])
        else:
            raise ValueError('The plex token has not been set for the {} ({}.{})'.format(
                self.name, __name__, type(self).__name__))

    def __init__(self, name, enabled):
        super().__init__(name, enabled)
        self.section = None
        self.plex = None
        self.url = DEFAULT_URL

    def scan(self):
        if self.section is None and 'SECTION' in self.props:
            self.section = self.props['SECTION']
        if self.section is None:
            raise ValueError('The section has not been set for the {} ({}.{})'.format(
                self.name, __name__, type(self).__name__))
        self.connect()

        albums = self.plex.library.section(self.section)
        for album in albums.all():
            # print(f'album: {album.title}')
            for photo in album.photos():
                # print(f'\tphoto: {photo.title}')

                path = photo.locations[0]
                ext_id = photo.ratingKey
                temp_photos = photo.download(tempfile.gettempdir())
                temp_photo_path = temp_photos[0]
                filename = os.path.basename(path)

                image_type = imghdr.what(temp_photo_path)
                if image_type is None:
                    logger.debug('Ignoring {} temporarily at {}'.format(path, temp_photo_path))
                else:
                    logger.info('Scanning {} temporarily at {}'.format(path, temp_photo_path))
                    file_hash = calc_hash(temp_photo_path)
                    file_info = FileInfo(filename, path, file_hash, temp_photo_path, ext_id)
                    for listener in self.listeners:
                        listener.on_file(self, file_info)
                        if os.path.exists(temp_photo_path):
                            os.remove(temp_photo_path)
