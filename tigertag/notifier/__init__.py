import logging
import os
import re

from collections import namedtuple
from tigertag import Pluggable
from tigertag.util import str2bool

logger = logging.getLogger(__name__)

NotificationInfo = namedtuple('NotificationInfo', 'subject message')


class Notifier(Pluggable):
    RESERVED_PROPS = ['NAME', 'ENABLED']

    def __init__(self, name, enabled):
        self.name = name
        self.enabled = enabled
        self.props = {}

    def notify(self, notification: NotificationInfo):
        raise NotImplementedError('The {} notifier has not implemented the notify method.'.format(self.name))


class NotifierManager:
    def __init__(self):
        self.notifiers = {}

    def add(self, notifier):
        self.notifiers[notifier.name] = notifier

    def notify(self, notification: NotificationInfo):
        if len(self.notifiers) == 0:
            logger.warning('No notifiers configured.  Please check your configuration')
        for notifier_name, notifier in self.notifiers.items():
            if notifier.enabled:
                notifier.notify(notification)

    def find_type(self, class_type):
        for notifier_name, notifier in self.notifiers.items():
            if isinstance(notifier, class_type):
                return notifier
        return None


class NotifierManagerBuilder:
    def __init__(self, notifier_manager_klass):
        self.notifier_manager_klass = notifier_manager_klass

    def build(self):
        raise NotImplementedError


class EnvironmentNotifierManagerBuilder(NotifierManagerBuilder):
    def __init__(self, notifier_manager_klass):
        super().__init__(notifier_manager_klass)

    def get_class(self, klass_name):
        parts = klass_name.split('.')
        module = ".".join(parts[:-1])
        m = __import__(module)
        for comp in parts[1:]:
            m = getattr(m, comp)
        return m

    def build(self):
        sm = self.notifier_manager_klass()
        notifier_detect = re.compile('^NOTIFIER_(?P<notifier>[A-Z0-9]*)_NAME')

        # Find and create the notifiers
        for env_name, env_value in os.environ.items():
            match = notifier_detect.match(env_name)
            if match is not None:
                logger.debug('Configuring notifier {}:{}'.format(env_name, env_value))
                notifier_env_name = match.group('notifier')
                notifier_klass_name = env_value
                enabled = False
                if os.environ['NOTIFIER_{}_ENABLED'.format(notifier_env_name)] is not None:
                    enabled = str2bool(os.environ['NOTIFIER_{}_ENABLED'.format(notifier_env_name)])
                notifier_klass = self.get_class(notifier_klass_name)
                notifier = notifier_klass(notifier_env_name, enabled)

                # Collect all the notifier properties
                prop_detect = re.compile('^NOTIFIER_{}_(?P<prop>[A-Z0-9_]*)'.format(notifier_env_name))
                for env_prop_name, env_prop_value in os.environ.items():
                    prop_match = prop_detect.match(env_prop_name)
                    if prop_match is not None:
                        prop_name = prop_match.group('prop')
                        if prop_name not in [Notifier.RESERVED_PROPS]:
                            notifier.props[prop_name] = env_prop_value
                sm.add(notifier)
        return sm
