import ckan
import ckan.plugins as plugins
import ckan.plugins.toolkit as tk
import datetime
import ckan.lib.helpers as h
from urlparse import urljoin
from dateutil.parser import parse
import pylons.config as config
from ckan.lib import mailer
from . import CommandBase
import logging

logger = None

class NotifyPublishedCommand(CommandBase):
    """
    """
    summary = __doc__.split('\n')[0]
    usage = __doc__
    max_args = 9
    min_args = 0

    def get_update_links(self, pkg_names):
        names = []
        for name in pkg_names:
            names.append(urljoin(config.get('ckan.site_url'),  
                                 h.url_for(controller='package',
                                 action='read',
                                 id=name)))
        return names

    def send_packages_update_mail(self, user, pkg_names):
        subject, body = self._generate_email('update_package_published.txt', datasets=pkg_names)
        mailer.mail_user(user, subject, body)
        logger.info("Email sent to %s.", user.name)

    def update_private_package(self, context, pkg_dict):
        if not pkg_dict.get('published_date'):
            return False
        # private dataset
        published_date = parse(pkg_dict['published_date'])
        today = datetime.date.today()
        if today < published_date.date():
            """published_date is later than today"""
            return False
        else:
            if not pkg_dict.get('process_state') or \
               pkg_dict.get('process_state') == 'Approved' and pkg_dict['private']:
                pkg_dict['private'] = False
                pkg_dict['state'] = 'active'
                datasets = tk.get_action('package_update')(
                            context=context, data_dict=pkg_dict)
                logger.info("Dataset '%s' is updated.", pkg_dict['name'])
                return True
            else:
                return False

    def get_org_admin(self, users_dict):
        admin_ids =[]
        for user in users_dict:
            if user['capacity'] == 'admin':
                admin_ids.append(user['id'])
        return admin_ids

    def __init__(self,name):
        CommandBase.__init__(self, name)
        self.PAGE_SIZE = 100

    def command(self):
        CommandBase.command(self)
        global logger
        logger = logging.getLogger('NotifyPublishedCommand')
         
        context = {'model': ckan.model,
           'session': ckan.model.Session,
           'ignore_auth': True}
        
        admin_user = tk.get_action('get_site_user')(context,{})
        updated_pkgs_name_sys_admin = []

        #get organizations
        published_context = {
                    'model': ckan.model,
                    'user':admin_user.get('name'),
                    'session': ckan.model.Session,
                    'ignore_auth': True
                }
        organizations = tk.get_action("organization_list")(published_context, data_dict={})
        if not organizations:
            raise("No organization exists")

        for org_name in organizations:
            # get all users in organization
            respond = tk.get_action("organization_show")(published_context, data_dict={"id": org_name})
            logger.info("In organization '%s'", org_name)
            if not respond.get("users"):
                logger.warn("No users in organization '%s'.", org_name)
            else:
                org_admin_ids = self.get_org_admin(respond.get("users"))
                updated_pkgs_name_org_admin = []

                for user in respond.get("users"):
                    q = { 'fq': "creator_user_id:{0} +owner_org:{1}".format(user['id'], respond.get("id")) }
                    if self._ckan_version_lt_26:
                        published_context['ignore_capacity_check'] = 'True'
                    else:
                        q.update(include_private = True)
                    search_results = tk.get_action("package_search")(published_context, data_dict=q)
                    try: 
                        pkgs = search_results['results']
                    except keyError:
                        continue
                    else:
                        updated_pkgs_name = [pkg['name'] for pkg in pkgs if self.update_private_package(published_context, pkg)]
                        if updated_pkgs_name:
                            updated_pkgs_name_org_admin.extend(updated_pkgs_name)
                            updated_pkgs_name_sys_admin.extend(updated_pkgs_name)
                            # send email to user
                            creator = ckan.model.User.get(user['id'])
                            self.send_packages_update_mail(creator, updated_pkgs_name)

            # send email to organization admins
            if updated_pkgs_name_org_admin:
                for org_adm_id in org_admin_ids:
                    o_adm = ckan.model.User.get(org_adm_id)
                    self.send_packages_update_mail(o_adm, updated_pkgs_name_org_admin)
            else:
                logger.info("No update for organization '%s'.", org_name)

            logger.info("Organization %s - done.\n", org_name)

        # send email to sys admin
        if updated_pkgs_name_sys_admin:
            admin_user_dict = tk.get_action("user_show")(data_dict={"id": admin_user.get('name')})
            admin_user = ckan.model.User.get(admin_user_dict.get('id'))
            self.send_packages_update_mail(admin_user, updated_pkgs_name_sys_admin)

        logger.info('All done')
