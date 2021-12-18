import logging
import os
import re

from collections import namedtuple
from tigertag.util import str2bool

logger = logging.getLogger(__name__)

FileInfo = namedtuple('FileInfo', 'name path hash temp ext_id')


class Scanner:
    RESERVED_PROPS = ['NAME', 'ENABLED']

    def __init__(self, name, enabled):
        self.name = name
        self.enabled = enabled
        self.props = {}
        self.listeners = []  # ScannerListeners

    def scan(self):
        raise NotImplementedError('The {} scanner has not implemented the scan method.'.format(self.name))


class ScannerListener:
    def on_file(self, scanner: Scanner, file_info: FileInfo):
        pass


class ScannerManager:
    def __init__(self):
        self.scanners = {}
        self.listeners = []  # ScannerListener array

    def add(self, scanner):
        self.scanners[scanner.name] = scanner

    def scan(self):
        if len(self.scanners) == 0:
            logger.warning('No scanners configured.  Please check your configuration')
        for scanner_name, scanner in self.scanners.items():
            if scanner.enabled:
                scanner.listeners = []
                for scanner_listener in self.listeners:
                    scanner.listeners.append(scanner_listener)
                scanner.scan()


class ScannerManagerBuilder:
    def __init__(self, scanner_manager_klass):
        self.scanner_manager_klass = scanner_manager_klass

    def build(self):
        raise NotImplementedError


class EnvironmentScannerManagerBuilder(ScannerManagerBuilder):
    def __init__(self, scanner_manager_klass):
        super().__init__(scanner_manager_klass)

    def get_class(self, klass_name):
        parts = klass_name.split('.')
        module = ".".join(parts[:-1])
        m = __import__(module)
        for comp in parts[1:]:
            m = getattr(m, comp)
        return m

    def build(self):
        sm = self.scanner_manager_klass()
        scanner_detect = re.compile('^SCANNER_(?P<scanner>[A-Z0-9]*)_NAME')

        # Find and create the scanners
        for env_name, env_value in os.environ.items():
            match = scanner_detect.match(env_name)
            if match is not None:
                logger.debug('Configuring scanner {}:{}'.format(env_name, env_value))
                scanner_env_name = match.group('scanner')
                scanner_klass_name = env_value
                enabled = False
                if os.environ['SCANNER_{}_ENABLED'.format(scanner_env_name)] is not None:
                    enabled = str2bool(os.environ['SCANNER_{}_ENABLED'.format(scanner_env_name)])
                scanner_klass = self.get_class(scanner_klass_name)
                scanner = scanner_klass(scanner_env_name, enabled)

                # Collect all the scanner properties
                prop_detect = re.compile('^SCANNER_{}_(?P<prop>[A-Z0-9_]*)'.format(scanner_env_name))
                for env_prop_name, env_prop_value in os.environ.items():
                    prop_match = prop_detect.match(env_prop_name)
                    if prop_match is not None:
                        prop_name = prop_match.group('prop')
                        if prop_name not in [Scanner.RESERVED_PROPS]:
                            scanner.props[prop_name] = env_prop_value
                sm.add(scanner)
        return sm
