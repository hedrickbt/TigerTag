import datetime
import logging
import sys

from tigertag.db import Persist
from tigertag.db import EnvironmentDbEngineBuilder
from tigertag.engine import EngineListener
from tigertag.engine import EngineManager
from tigertag.engine import EnvironmentEngineManagerBuilder
from tigertag.scanner import EnvironmentScannerManagerBuilder
from tigertag.scanner import ScannerListener
from tigertag.scanner import ScannerManager

# SCANNER_DIRECTORY_NAME=tigertag.scanner.directory.DirectoryScanner
# SCANNER_DIRECTORY_ENABLED=True
# SCANNER_DIRECTORY_PATH=data/images/input
# ENGINE_IMAGGA_NAME=tigertag.engine.imagga.ImaggaEngine
# ENGINE_IMAGGA_ENABLED=True
# ENGINE_IMAGGA_API_KEY=<VALUE>
# ENGINE_IMAGGA_API_SECRET=<VALUE>
# ENGINE_IMAGGA_API_URL=https://api.imagga.com/v2
# DB_URL=sqlite:///tigertag.db

logger = logging.getLogger(__name__)
FOUND_TAGS = {}
FOUND_FILES = {}
engine_manager = None
persist = None


def on_tags(engine, tag_info):
    FOUND_TAGS[tag_info['file_path']] = tag_info


def on_file(scanner, file_info):
    tag_it = True
    temp_date_time = datetime.datetime.now()
    resource = persist.get_resource_by_location(file_info['file_path'])
    if resource is not None:
        if resource['hashval'] == file_info['file_hash']:
            logger.debug('Hash did not change.  Will NOT tag {}'.format(file_info['file_path']))
            tag_it = False
    persist.set_resource(
        file_info['file_name'],
        file_info['file_path'],
        file_info['file_hash'],
        temp_date_time
    )
    if tag_it:
        logger.debug('New file or hash changed.  Will tag {}'.format(file_info['file_path']))
        engine_manager.tag(file_info['file_path'])


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

    sl = ScannerListener()
    sl.on_file = on_file
    smb = EnvironmentScannerManagerBuilder(ScannerManager)
    sm = smb.build()
    sm.listeners.append(sl)
    sm.scan()

    print(FOUND_TAGS)
