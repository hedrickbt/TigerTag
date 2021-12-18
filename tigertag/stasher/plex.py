import logging

from plexapi.server import PlexServer

from tigertag.engine import Engine
from tigertag.stasher import Stasher

logger = logging.getLogger(__name__)
DEFAULT_URL = 'http://127.0.0.1:32400'

class PlexStasher(Stasher):
    def connect(self):
        if 'TOKEN' in self.props:
            if 'URL' in self.props:
                self.url = self.props['URL']
            self.plex = PlexServer(self.url, self.props['TOKEN'])
        else:
            raise ValueError(f'The plex token has not been set for the '
                             f'{self.name} ({__name__}.{type(self).__name__}')

        if 'SECTION' in self.props:
            self.section = self.props['SECTION']
        else:
            raise ValueError(f'The plex section has not been set for the '
                             f'{self.name} ({__name__}.{type(self).__name__}.  '
                             f'The SECTION property is missing)')

        self.connected = True

    def __init__(self, name, enabled):
        super().__init__(name, enabled)
        self.section = None
        self.plex = None
        self.url = DEFAULT_URL
        self.connected = False

    def stash(self, engine: Engine, path: str, tags: dict, ext_id: str):
        # currently only the plex scanner sets an ext_id
        if ext_id is not None:
            if not self.connected:
                self.connect()

            logger.debug(f'Looking up photo ekey/ratingKey: {ext_id}')
            for photo in self.plex.library.section(self.section).fetchItem(ext_id):
                # Get just the tag values, not the Tag objects
                orig_plex_tags = sorted(list(map(lambda x: x.tag, photo.tags)))

                remove_tags = sorted(
                    list(
                        # These lower call are silly.  For some reason even though Plex stores
                        # the tag as you send it - say tti_MyTag - instead it returns it with the first
                        # letter always upper-cased - ex Tti_MyTag.  But remove and add operations on
                        # tags do not do that - only when you ask for the photos' tags.
                        filter(lambda tag: tag.lower().startswith(f'{engine.prefix.lower()}_'), orig_plex_tags)
                    )
                )
                logger.debug(f'{engine.name} removing tags for "{self.section}":{path}: {",".join(remove_tags)}')
                photo.removeTag(remove_tags, False)
                photo.reload()  # without this the add tags will add them back
                new_plex_tags = sorted(list(tags.keys()))
                logger.debug(f'{engine.name} add tags for "{self.section}":{path}: {",".join(new_plex_tags)}')
                photo.addTag(new_plex_tags, False)
