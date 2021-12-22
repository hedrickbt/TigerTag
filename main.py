import datetime
import logging
import logging.handlers
import sys
import traceback

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
from tigertag.notifier import NotifierManager
from tigertag.notifier import EnvironmentNotifierManagerBuilder
from tigertag.notifier import NotificationInfo
from tigertag.notifier.email import EmailNotifier

# SCANNER_DIRECTORY_NAME=tigertag.scanner.directory.DirectoryScanner
# SCANNER_DIRECTORY_ENABLED=True
# SCANNER_DIRECTORY_PATH=data/images/input

# SCANNER_PLEX_NAME=tigertag.scanner.plex.PlexScanner
# SCANNER_PLEX_ENABLED=True
# SCANNER_PLEX_TOKEN=<VALUE>
# SCANNER_PLEX_URL=<VALUE ex: http://127.0.0.1:32400>
# SCANNER_PLEX_SECTION=<VALUE ex: TEST Family Photos>
# ENGINE_IMAGGA_NAME=tigertag.engine.imagga.ImaggaEngine
# ENGINE_IMAGGA_PREFIX=Tti
# ENGINE_IMAGGA_ENABLED=True
# ENGINE_IMAGGA_API_KEY=<VALUE>
# ENGINE_IMAGGA_API_SECRET=<VALUE>
# ENGINE_IMAGGA_API_URL=https://api.imagga.com/v2
# STASHER_CONSOLE_NAME=tigertag.stasher.console.ConsoleStasher
# STASHER_CONSOLE_ENABLED=True
# STASHER_PLEX_NAME=tigertag.stasher.plex.PlexStasher
# STASHER_PLEX_ENABLED=True
# STASHER_PLEX_TOKEN=<VALUE>
# STASHER_PLEX_URL=<VALUE ex: http://127.0.0.1:32400>
# STASHER_PLEX_SECTION=<VALUE ex: TEST Family Photos>
# DB_URL=sqlite:///data/db/tigertag.db
# ENGINE_COMPREFACE_NAME=tigertag.engine.compreface.ComprefaceEngine
# ENGINE_COMPREFACE_PREFIX=ttf
# ENGINE_COMPREFACE_ENABLED=True
# ENGINE_COMPREFACE_API_KEY=<VALUE ex: 5b3448dc-f46...>
# ENGINE_COMPREFACE_API_PORT=8000
# ENGINE_COMPREFACE_API_URL=http://localhost
# ENGINE_COMPREFACE_FACES_FOLDER=data/faces
# ENGINE_COMPREFACE_FACES_CONFIG=data/faces/faces.yaml
# NOTIFIER_EMAIL_NAME=tigertag.notifier.email.EmailNotifier
# NOTIFIER_EMAIL_ENABLED=True
# NOTIFIER_EMAIL_FROM=<ex: your-from-address@gmail.com>
# NOTIFIER_EMAIL_TO=<ex: your-to-address@gmail.com>
# NOTIFIER_EMAIL_SERVER=<ex: smtp.gmail.com>
# NOTIFIER_EMAIL_PORT=<ex: 587>
# NOTIFIER_EMAIL_SSL=<ex: False>
# NOTIFIER_EMAIL_STARTTLS=<ex: True>
# NOTIFIER_EMAIL_USERNAME=<ex: your-from-address@gmail.com>
# NOTIFIER_EMAIL_PASSWORD=<email account password>


MIN_CONFIDENCE = 30

logger = logging.getLogger(__name__)
FOUND_TAGS: dict[str, TagInfo] = {}
FOUND_FILES: dict[str, FileInfo] = {}
notifier_manager: NotifierManager = None
engine_manager: EngineManager = None
stasher_manager: StasherManager = None
persist: Persist = None


def on_tags(engine: Engine, tag_info: TagInfo, ext_id: str):
    if tag_info.tags is not None:
        new_tags = dict(filter(lambda elem: elem[1]['confidence'] >= MIN_CONFIDENCE, tag_info.tags.items()))
        new_tag_info = TagInfo(tag_info.path, new_tags)
        FOUND_TAGS[tag_info.path] = new_tag_info
        persist.set_resource(
            tag_info.path,
            engine=engine.name,
            tags=new_tags
        )
        stasher_manager.stash(engine, tag_info.path, new_tags, ext_id)
    else:
        persist.set_resource_rescan(tag_info.path)


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
        engine_manager.tag(file_info.path, file_info.temp, file_info.ext_id)


def add_smtp_logging_handler():
    email_notifier: EmailNotifier = notifier_manager.find_type(EmailNotifier)
    if email_notifier is not None:
        temp_credentials = email_notifier.get_credentials()
        credentials = None
        if temp_credentials is not None:
            credentials = (temp_credentials.username, temp_credentials.password)
        smtp_handler = logging.handlers.SMTPHandler(
            mailhost=(email_notifier.get_prop('SERVER'), email_notifier.get_prop('PORT')),
            fromaddr=email_notifier.get_prop('FROM'),
            toaddrs=email_notifier.get_prop('TO'),
            subject='TigerTag Error',
            credentials=credentials,
            secure=())
        smtp_handler.setLevel(logging.ERROR)
        logging.getLogger().addHandler(smtp_handler)  # add global smtp handler
        # logger.addHandler(smtp_handler)  # this would only add the handler to the logger in main.py


if __name__ == "__main__":
    nmb = EnvironmentNotifierManagerBuilder(NotifierManager)
    notifier_manager = nmb.build()
    notifier_manager.notify(NotificationInfo('TigerTag', 'Scan Started'))

    try:
        logging.basicConfig(
            stream=sys.stderr,
            level=logging.DEBUG,
            format='%(asctime)s %(levelname)-8s %(name)s : %(funcName)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S')
        add_smtp_logging_handler()

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

        notifier_manager.notify(NotificationInfo('TigerTag', 'Scan Complete'))
    except Exception as e:
        logger.error(f'{e}\n{traceback.format_exc()}')
        raise e
