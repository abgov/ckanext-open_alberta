from ckan.lib.cli import CkanCommand
from ckan.plugins import toolkit
import ckan.lib.mailer as mailer
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
        query = {
            'fq': 
        }
        packages = package_search(None, query)
        subject, body = generate_email('base.txt', 
                                       subject='Datasets due for review',
                                       user_name='Greg Burek')
