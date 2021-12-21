import logging
import smtplib

from tigertag.notifier import Notifier
from tigertag.notifier import NotificationInfo
from tigertag.util import str2bool

logger = logging.getLogger(__name__)


class EmailNotifier(Notifier):
    def __init__(self, name, enabled):
        super().__init__(name, enabled)
        self.from_address = None
        self.to = None
        self.server = None
        self.port = None
        self.ssl = False
        self.starttls = False

    def _setup(self):
        if self.server is None:
            self.from_address = self.get_prop('FROM')
            self.to = self.get_prop('TO')
            self.server = self.get_prop('SERVER')
            self.port = int(self.get_prop('PORT'))
            self.ssl = str2bool(self.get_prop('SSL'))
            self.starttls = str2bool(self.get_prop('STARTTLS'))

    def notify(self, notification: NotificationInfo):
        self._setup()
        if self.ssl:
            server = smtplib.SMTP_SSL(self.server, self.port)
        else:
            server = smtplib.SMTP(self.server, self.port)
        server.ehlo()
        if self.starttls:
            server.starttls()
        if self.get_prop('USERNAME', '') != '' and self.get_prop('PASSWORD', '') != '':
            server.login(self.get_prop('USERNAME'), self.get_prop('PASSWORD'))
        message = 'Subject: {}\n\n{}'.format(notification.subject, notification.message)
        server.sendmail(self.from_address, self.to, message)

        logger.info(f'Notification sent {notification.subject}')