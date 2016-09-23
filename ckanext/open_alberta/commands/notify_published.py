import sys
from ckan.lib.cli import CkanCommand
import ckan.logic as logic
import ckan
import ckan.plugins as plugins
import ckan.plugins.toolkit as tk
import datetime
import ckan.lib.helpers as h
import ckan.lib.mailer as mailer
from urlparse import urljoin
from dateutil.parser import parse
import pylons.config as config
from ckan.lib.base import render_jinja2
import time
import datetime
import logging

log = logging.getLogger(__name__)
ValidationError = logic.ValidationError

def get_update_links(pkg_names):
    names = []
    for name in pkg_names:
        names.append(urljoin(config.get('ckan.site_url'),  
                             h.url_for(controller='package',
                             action='read',
                             id=name)))
    return names

def get_update_package_body(user, pkg_names):
    extra_vars = {
        'update_links': get_update_links(pkg_names),
        'site_title': config.get('ckan.site_title'),
        'site_url': config.get('ckan.site_url'),
        'user_name': user.name
        }
    # NOTE: This template is translated
    return render_jinja2('emails/update_package_published.txt', extra_vars)

def send_packages_update_mail(user, pkg_names):
    body = get_update_package_body(user, pkg_names)
    extra_vars = {
        'site_title': config.get('ckan.site_title')
    }
    subject = render_jinja2('emails/update_package_published_subject.txt', extra_vars)
    # Make sure we only use the first line
    subject = subject.split('\n')[0]
    mailer.mail_user(user, subject, body)
    log.debug("Email sent to {0}.".format(user.name))
    

def update_private_package(context, pkg_dict):
    if not pkg_dict.get('published_date'):
        return False
    # private dataset
    date_published = parse(pkg_dict['published_date'])
    today = datetime.datetime.now()
    if today < date_published:
        """date_published is later than today"""
        return False
    else:
        pkg_dict['private'] = False
        pkg_dict['state'] = 'active'
        try:
            datasets = tk.get_action('package_update')(
                    context=context, data_dict=pkg_dict)
        except ValidationError, e:
            log.debug("Dataset '{0}' is NOT validated for update.".format(pkg_dict['name']))
        else:
            log.debug("Dataset '{0}' is updated.".format(pkg_dict['name']))
    return True

class NotifyPublishedCommand(CkanCommand):
    '''
      This class is used for paster command to auto update packages based on the
      published date. If the date is before or the same day of current date, the 
      package will be auto updated and email will be sent to user, org_admin and
      sys_admin.
    '''
    summary = __doc__.split('\n')[0]
    usage = __doc__
    max_args = 9
    min_args = 0
    
    def __init__(self,name):
        super(NotifyPublishedCommand,self).__init__(name)

    def command(self):
        log.debug(str(datetime.datetime.now()))
        start_time = time.time()
        self._load_config()
         
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
            log.debug("No organization exists")
            raise("No organization exists")

        for org_name in organizations:
            # get all users in organization
            respond = tk.get_action("organization_show")(published_context, data_dict={"id": org_name})
            log.debug("In organization '{0}'".format(org_name))
            if not respond.get("users"):
                log.debug("No user in origanization '{0}'.".format(org_name))
            else:
                org_admin_ids = [ user['id']  for user in respond.get("users") if user['capacity'] == 'admin' ]
                updated_pkgs_name_org_admin = []

                for user in respond.get("users"):
                    #check private datasets for the user
                    q = {
                        'include_private': 'true',
                        'fq': "private:true"
                    }
                    q['fq'] = "{0} +creator_user_id:{1} +owner_org:{2}".format(q['fq'], user['id'], respond.get("id"))
                    search_results = tk.get_action("package_search")(published_context, data_dict=q)
                    try: 
                        pkgs = search_results['results']
                    except keyError:
                        continue
                    else:
                        updated_pkgs_name = [pkg['name'] for pkg in pkgs if update_private_package(published_context, pkg)]
                        if updated_pkgs_name:
                            updated_pkgs_name_org_admin.extend(updated_pkgs_name)
                            updated_pkgs_name_sys_admin.extend(updated_pkgs_name)
                            # send email to user
                            creator = ckan.model.User.get(user['id'])
                            send_packages_update_mail(creator, updated_pkgs_name)

            # send email to organization admins
            if updated_pkgs_name_org_admin:
                for org_adm_id in org_admin_ids:
                    o_adm = ckan.model.User.get(org_adm_id)
                    send_packages_update_mail(o_adm, updated_pkgs_name_org_admin)
            else:
                log.debug("No update for origanization '{0}'.".format(org_name))

            log.debug("Origanization {0} are done.\n".format(org_name))

        # send email to sys admin
        if updated_pkgs_name_sys_admin:
            admin_user_dict = tk.get_action("user_show")(data_dict={"id": admin_user.get('name')})
            admin_user = ckan.model.User.get(admin_user_dict.get('id'))
            send_packages_update_mail(admin_user, updated_pkgs_name_sys_admin)

        run_time = time.strftime("%H:%M:%S", time.gmtime(time.time() - start_time))
        log.debug("Run time: ".format(run_time))
        log.debug('All done')
