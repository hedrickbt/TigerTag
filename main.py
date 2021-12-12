import logging
import os
import sys

from tigertag.engine import EngineListener
from tigertag.engine import EngineManager
from tigertag.engine import EnvironmentEngineManagerBuilder
from tigertag.scanner import ScannerListener
from tigertag.scanner import ScannerManager
from tigertag.scanner import EnvironmentScannerManagerBuilder

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


def on_tags(engine, tag_info):
    FOUND_TAGS[tag_info['file_path']] = tag_info


def on_file(scanner, file_info):
    em.tag(file_info['file_path'])


if __name__ == "__main__":
    logging.basicConfig(
        stream=sys.stderr,
        level=logging.INFO,
        format='%(asctime)s %(levelname)-8s %(name)s : %(funcName)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')

    el = EngineListener()
    el.on_tags = on_tags
    emb = EnvironmentEngineManagerBuilder(EngineManager)
    em = emb.build()
    em.listeners.append(el)

    sl = ScannerListener()
    sl.on_file = on_file
    smb = EnvironmentScannerManagerBuilder(ScannerManager)
    sm = smb.build()
    sm.listeners.append(sl)
    sm.scan()

    print(FOUND_TAGS)
