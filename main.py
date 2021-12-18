import datetime
import logging
import sys

from tigertag.db import EnvironmentDbEngineBuilder
from tigertag.db import Persist
from tigertag.engine import Engine
from tigertag.engine import EngineListener
from tigertag.engine import EngineManager
from tigertag.engine import EnvironmentEngineManagerBuilder
from tigertag.engine import TagInfo
from tigertag.scanner import EnvironmentScannerManagerBuilder
from tigertag.scanner import FileInfo
from tigertag.scanner import Scanner
from tigertag.scanner import ScannerListener
from tigertag.scanner import ScannerManager
from tigertag.stasher import StasherManager
from tigertag.stasher import EnvironmentStasherManagerBuilder

# SCANNER_DIRECTORY_NAME=tigertag.scanner.directory.DirectoryScanner
# SCANNER_DIRECTORY_ENABLED=True
# SCANNER_DIRECTORY_PATH=data/images/input
# SCANNER_PLEX_NAME=tigertag.scanner.plex.PlexScanner
# SCANNER_PLEX_ENABLED=True
# SCANNER_PLEX_TOKEN=<VALUE>
# SCANNER_PLEX_URL=<VALUE ex: http://127.0.0.1:32400>
# SCANNER_PLEX_SECTION=<VALUE ex: TEST Family Photos>
# ENGINE_IMAGGA_NAME=tigertag.engine.imagga.ImaggaEngine
# ENGINE_IMAGGA_PREFIX=tti
# ENGINE_IMAGGA_ENABLED=True
# ENGINE_IMAGGA_API_KEY=<VALUE>
# ENGINE_IMAGGA_API_SECRET=<VALUE>
# ENGINE_IMAGGA_API_URL=https://api.imagga.com/v2
# STASHER_CONSOLE_NAME=tigertag.stasher.console.ConsoleStasher
# STASHER_CONSOLE_ENABLED=True
# DB_URL=sqlite:///tigertag.db
MIN_CONFIDENCE = 30

logger = logging.getLogger(__name__)
FOUND_TAGS: dict[str, TagInfo] = {}
FOUND_FILES: dict[str, FileInfo] = {}
engine_manager: EngineManager = None
stasher_manager: StasherManager = None
persist: Persist = None


def on_tags(engine: Engine, tag_info: TagInfo):
    new_tags = dict(filter(lambda elem: elem[1]['confidence'] >= MIN_CONFIDENCE, tag_info.tags.items()))
    new_tag_info = TagInfo(tag_info.path, new_tags)
    FOUND_TAGS[tag_info.path] = new_tag_info
    persist.set_resource(
        tag_info.path,
        engine=engine.name,
        tags=new_tags
    )
    stasher_manager.stash(engine, tag_info.path, new_tags)


def on_file(scanner: Scanner, file_info: FileInfo):
    tag_it = True
    temp_date_time = datetime.datetime.now()
    resource = persist.get_resource_by_location(file_info.path)
    if resource is not None:
        if resource['hashval'] == file_info.hash:
            logger.debug('Hash did not change.  Will NOT tag {}'.format(file_info.path))
            tag_it = False
    if tag_it:
        logger.debug('New file or hash changed.  Will tag {}'.format(file_info.path))
        persist.set_resource(
            file_info.path,
            file_info.name,
            file_info.hash,
            temp_date_time
        )
        engine_manager.tag(file_info.path)


if __name__ == "__main__":
    logging.basicConfig(
        stream=sys.stderr,
        level=logging.DEBUG,
        format='%(asctime)s %(levelname)-8s %(name)s : %(funcName)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')

    deb = EnvironmentDbEngineBuilder()
    de = deb.build()
    persist = Persist(de)

    el = EngineListener()
    el.on_tags = on_tags
    emb = EnvironmentEngineManagerBuilder(EngineManager)
    engine_manager = emb.build()
    engine_manager.listeners.append(el)

    stmb = EnvironmentStasherManagerBuilder(StasherManager)
    stasher_manager = stmb.build()

    sl = ScannerListener()
    sl.on_file = on_file
    smb = EnvironmentScannerManagerBuilder(ScannerManager)
    sm = smb.build()
    sm.listeners.append(sl)

    sm.scan()
