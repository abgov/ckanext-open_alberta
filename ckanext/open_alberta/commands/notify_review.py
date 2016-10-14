from ckan.lib.cli import CkanCommand
from ckan.plugins import toolkit
from ckan.exceptions import CkanVersionException
import ckan.lib.mailer as mailer
from datetime import date
from dateutil.relativedelta import relativedelta
from . import generate_email

class ReviewDueNotifyCommand(CkanCommand):
    '''
    '''
    summary = __doc__.split('\n')[0]
    usage = __doc__
    max_args = 1
    min_args = 0

    def __init__(self,name):
        super(ReviewDueNotifyCommand,self).__init__(name)

    def command(self):
        self._load_config()

        package_search = toolkit.get_action('package_search')
        tomorrow = date.today()+relativedelta(days=1)
        ctx = {
            'ignore_auth': True
        }
        admin_user = toolkit.get_action('get_site_user')(ctx, {})
        ctx['user'] = admin_user['name']
        try:
            toolkit.requires_ckan_version('2.6')
            query = {
                'include_private': True,
                'fq': tomorrow.strftime('next_review_date:[* TO %Y-%m-%dT%XZ]')
            }
        except CkanVersionException:
            # CKAN < 2.6
            ctx['ignore_capacity_check'] = 'True' # include private packages
            query = {
                'fq': tomorrow.strftime('next_review_date:[* TO %Y-%m-%dT%XZ]')
            }
        
        packages = package_search(ctx, query)
        from pprint import PrettyPrinter
        pp = PrettyPrinter()
        print 'Query:'
        pp.pprint(query)
        print 'Results: ', packages['count']
        for pkg in packages['results']:
            print pkg['name'], pkg['next_review_date']
            pp.pprint(pkg)

        subject, body = generate_email('base.txt', 
                                       subject='Datasets due for review',
                                       user_name='Greg Burek',
                                       datasets=packages)
