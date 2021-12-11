import logging

logger = logging.getLogger(__name__)


class ScannerListener:
    def on_file(self, scanner, file_info):
        pass


class Scanner:
    def __init__(self, name, enabled):
        self.name = name
        self.enabled = enabled
        self.props = {}
        self.listeners = []  # ScannerListeners

    def scan(self):
        raise NotImplementedError('The {} scanner has not implemented the scan method.'.format(self.name))


class ScannerManager:
    def __init__(self):
        self.scanners = {}
        self.listeners = []  # ScannerListener array

    def add(self, scanner):
        self.scanners[scanner.name] = scanner

    def scan(self):
        for scanner_name, scanner in self.scanners.items():
            if scanner.enabled:
                for scanner_listener in self.scanners:
                    scanner.listeners.append(scanner_listener)
                scanner.scan()
