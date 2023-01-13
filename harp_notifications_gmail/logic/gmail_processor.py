import harp_notifications_gmail.settings as settings
from logger.logging import service_logger
from harp_notifications_gmail.logic.email_template import template
import smtplib
import ssl
import email.utils
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from harp_notifications_gmail.logic.get_bot_config import bot_config
from harp_notifications_gmail.metrics.service_monitoring import Prom

log = service_logger()


class GmailNotifications(object):
    def __init__(self, recipients: list, email_subject: str, email_body: str, email_user, email_password):
        self.recipients = recipients
        self.email_subject = email_subject
        self.email_body = email_body
        self.email_user = email_user
        self.email_password = email_password
        self.smtp = None
        self.bot_config = self.get_bot_config()

    def get_bot_config(self):
        if self.email_user:
            config = {
                'EMAIL_USER': self.email_user,
                'EMAIL_PASSWORD': self.email_password
            }
        else:
            config = bot_config(bot_name='email')

        return config

    def email_template(self):
        html = template.replace("{email_body}", self.email_body)

        return html

    def prepare_email(self):
        msgroot = MIMEMultipart('related')
        msgroot['From'] = self.bot_config['EMAIL_USER']
        msgroot['To'] = ', '.join(self.recipients)
        msgroot['Subject'] = self.email_subject

        log.info(
            msg=f"Email should be created",
            extra={'tags': {}})

        msgroot["Message-ID"] = email.utils.make_msgid()
        msgroot.preamble = 'This is a multi-part message in MIME format.'
        msgalternative = MIMEMultipart('alternative')
        msgroot.attach(msgalternative)
        msgtext = MIMEText(self.email_template(), 'html')

        msgalternative.attach(msgtext)

        return msgroot

    def smtp_connection(self):
        try:
            log.info(msg=f"Connecting to {settings.EMAIL_HOST}:{settings.EMAIL_PORT} User: {self.bot_config['EMAIL_USER']} Password: {self.bot_config['EMAIL_PASSWORD']}")
            ssl_context = ssl._create_unverified_context()
            self.smtp = smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT, context=ssl_context)
            self.smtp.login(user=self.bot_config['EMAIL_USER'], password=self.bot_config['EMAIL_PASSWORD'])
            log.info(
                msg=f"Connected to SMTP",
                extra={'tags': {}})
        except Exception as err:
            log.error(
                msg=f"Can`t connect to SMTP:{err}",
                extra={'tags': {}})

    @Prom.SEND_GMAIL_NOTIFICATION.time()
    def create_email(self):
        self.smtp_connection()
        try:
            msgroot = self.prepare_email()

            self.smtp.sendmail(self.bot_config['EMAIL_USER'], self.recipients, msgroot.as_string())
            self.smtp.close()

            log.info(msg=f"Email has been sent to {self.bot_config['EMAIL_USER']}")

        except (smtplib.SMTPServerDisconnected, smtplib.SMTPSenderRefused) as err:
            log.error(
                msg=f"Can`t send email: {err}",
                extra={'tags': {}})

        return {'status': 'success'}
