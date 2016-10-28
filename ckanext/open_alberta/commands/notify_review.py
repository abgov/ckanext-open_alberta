from ckan.plugins import toolkit
from ckan.lib import mailer
from datetime import date
from dateutil.relativedelta import relativedelta
import logging
from . import CommandBase


class ReviewDueNotifyCommand(CommandBase):
    """ This is to be run from a cron job to send email notifications iabout datasets being due for review
        to the editors and admins of relevant organizations.
        Usage: paster --plugin ckanext-open_alberta notify_review -c <config file>
    """
    summary = __doc__.split('\n')[0]
    usage = __doc__
    max_args = 1
    min_args = 0

    def __init__(self, name):
        CommandBase.__init__(self, name)
        self.PAGE_SIZE = 1000

    def command(self):
        CommandBase.command(self)
        logger = logging.getLogger('ReviewDueNotifyCommand')
        logger.info("Starting the review notify task")

        package_search = toolkit.get_action('package_search')
        tomorrow = date.today()+relativedelta(days=1)
        ctx = { 'ignore_auth': True }
        admin_user = toolkit.get_action('get_site_user')(ctx, {})
        ctx['user'] = admin_user['name']
        query = {
            'fq': tomorrow.strftime('next_review_date:[* TO %Y-%m-%dT%XZ]'),
            'start': 0,
            'rows': self.PAGE_SIZE
        }

        if self._ckan_version_lt_26:
            ctx['ignore_capacity_check'] = 'True' # include private packages
        else:
            query.update(include_private = True)

        orgs = self._get_orgs(ctx)
        done = False

        while not done:
            #logger.debug('start=%s', query['start'])
            response = package_search(ctx, query)
            #logger.debug('Got %s datasets, %s total', len(response['results']), response['count'])
            if response['count'] == 0:
                logger.info('No due for review packages found')
                return
            for pkg in response['results']:
                orgid = pkg['organization']['id']
                if orgid in orgs:
                    orgs[orgid]['datasets'].append({'id': pkg['name'],
                                                    'title': pkg['title']})
                else:
                    logger.warn('Package %s owner organization %s was not found - skipping', 
                                pkg['name'], pkg['organization']['name'])
            query['start'] += self.PAGE_SIZE
            done = len(response['results']) < self.PAGE_SIZE

        for orgdata in orgs.itervalues():
            if len(orgdata['datasets']) > 0:
                logger.info('Found %s datasets due for review owned by organization %s', 
                            len(orgdata['datasets']), orgdata['orgname'])
                for user in orgdata['editors']:
                    logger.info('Sending email notification to <%s> %s', user['name'], user['email'])
                    subject, body = self._generate_email('packages_due_for_review.txt', 
                                                         datasets=orgdata['datasets'], user_name=user['name'])
                    mailer.mail_recipient(user['fullnm'], user['email'], subject, body)
        logger.info('All done')

    def _get_orgs(self, ctx):
        """ Reads all needed organization and user data """
        orgs = toolkit.get_action('organization_list')(ctx, {'all_fields': True,
                                                             'include_users': True})
        get_user = toolkit.get_action('user_show')
        ret = {}
        for org in orgs:
            orgid = org['id']
            ret[orgid] = {'editors': [], 'datasets': [], 'orgname': org['name']}
            for u in org['users']:
                if u['capacity'] in ('admin', 'editor'):
                    usr = get_user(ctx, {'id': u['id']})
                    usrdict = {'name': usr['name'],
                               'fullnm': usr['display_name'],
                               'email': usr['email']}
                    ret[orgid]['editors'].append(usrdict)
        return ret
