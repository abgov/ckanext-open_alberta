""" commands module - various commands used by Open Alberta
"""

from pylons import config
from ckan.plugins import toolkit
from ckan.lib import helpers
import ckan.lib.mailer
from ckan.lib.cli import CkanCommand
from ckan.exceptions import CkanVersionException

class CommandBase(CkanCommand):
    """ Base functionality used by commands """
    def __init__(self, nm):
        super(CkanCommand, self).__init__(nm)
        self._ckan_version_lt_26 = False
        try:
            toolkit.requires_ckan_version('2.6')
        except CkanVersionException:
            self._ckan_version_lt_26 = True
            # CKAN v2.5.3's mailer has references to the global context and also adds hard-coded 'niceties' to the email.
            # That has been removed in 2.6.
            # Monkey patch so we don't get errors from app_globals not being there and
            # there is no unwanted hard-coded email message content
            def skip_niceties(recipient_name, body, sender_name, sender_url):
                return body
            def mail_recipient(recipient_name, recipient_email, subject, body, headers={}):
                # This is pretty much a copy of mail_recipient from CKAN 2.6
                from ckan.lib.mailer import _mail_recipient
                site_title = config.get('ckan.site_title')
                site_url = config.get('ckan.site_url')
                return _mail_recipient(recipient_name, recipient_email,
                                       site_title, site_url, subject, body, headers=headers)
            ckan.lib.mailer.add_msg_niceties = skip_niceties
            ckan.lib.mailer.mail_recipient = mail_recipient

    def command(self):
        self._load_config()

    def _generate_email(self, template_nm, **kwargs):
        """ Renders the requested jinja template from 'emails' folder.
            Returns (subject, body) """
        env = config['pylons.app_globals'].jinja_env
        template = env.get_template('emails/'+template_nm)
        template.globals.update(h=helpers, c=config)
        lines = [ln for ln in template.generate(kwargs)]
        subject = lines[0]
        body = ''.join(lines[1:])
        return subject, body

