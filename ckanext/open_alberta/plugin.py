import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckanext.open_alberta import helpers
import pylons.config as config
import datetime
import dateutil.parser as parser
from ckan.common import _

@toolkit.side_effect_free
def counter_on_off(context, data_dict=None):
    # Get the value of the ckan.open_alberta.counter_on
    # setting from the CKAN config file as a string, or False if the setting
    # isn't in the config file.
    counter_on = config.get('ckan.open_alberta.counter_on', False)
    # Convert the value from a string to a boolean.
    counter_on = toolkit.asbool(counter_on)
    return {"counter_on": counter_on}


def latest_datasets():
    '''Return latest datasets.'''

    datasets = toolkit.get_action('package_search')(
        data_dict={'rows': 4, 'sort': 'metadata_created desc' })

    return datasets['results']

def check_archive_date(archive_date=""):
    """ Return false if archive_date is empty or later than today.
        Otherwise, return true.  
    """
    if archive_date == "":
        return False
    today = datetime.datetime.now()
    archive_date = parser.parse(archive_date)
    if today < archive_date:
        return False
    return True

class OpenAlbertaPagesPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.IConfigurer, inherit=True)
    plugins.implements(plugins.IConfigurable, inherit=False)

    def configure(self, config):
        from model import setup
        setup()

    def update_config(self, config):
        config['ckan.resource_proxy_enabled'] = True

    def before_map(self, m):

        m.connect('suggest' ,'/suggest',
                    controller='ckanext.open_alberta.controller:SuggestController',
                    action='suggest_form')

        m.connect('contact' ,'/contact',
                    controller='ckanext.open_alberta.controller:SuggestController',
                    action='contact_form')

        m.connect('policy' ,'/policy',
                    controller='ckanext.open_alberta.controller:PagesController',
                    action='policy')

        m.connect('licence' ,'/licence',
                    controller='ckanext.open_alberta.controller:PagesController',
                    action='licence')

# /content/government-alberta-open-information-and-open-data-policy > /policy
        m.redirect('/content/government-alberta-open-information-and-open-data-policy', 
                   '/policy',
                   _redirect_code='301 Moved Permanently')

        m.redirect('/faq', '/interact/faq',
                     _redirect_code='301 Moved Permanently')

# /blog > /interact/
        m.redirect('/blog', '/interact',
                     _redirect_code='301 Moved Permanently')

        m.redirect('/blog/{url:.*}', '/interact/{url}',
                     _redirect_code='301 Moved Permanently')

# /apps-for-alberta > /interact/apps-for-alberta
        m.redirect('/apps-for-alberta', '/interact/apps-for-alberta',
                     _redirect_code='301 Moved Permanently')

# /visualization(s) > /interact/visualization
        m.redirect('/visualizations', '/interact/visualizations',
                     _redirect_code='301 Moved Permanently')
        m.redirect('/visualization', '/interact/visualizations',
                     _redirect_code='301 Moved Permanently')

# /data > /datasets
        m.redirect('/data/{url:.*}', '/dataset/{url}',
                     _redirect_code='301 Moved Permanently')

# /documents > /documentation
        m.redirect('/documents/{url:.*}', '/documentation/{url}',
                     _redirect_code='301 Moved Permanently')

        return m


import ckan.controllers.admin as admin
import ckan.controllers.home as home

_orig__get_config_form_items = admin.AdminController._get_config_form_items
_orig_home_index = home.HomeController.index

def patch_ckan_admin():
    def _get_config_form_items_patched(self):
        """ This function alters the data created by intenal CKAN admin config code.
            The following is done:
              1. Homepage layout labels are replaced
              2. New input with redirect url is added.
        """
        ret = _orig__get_config_form_items(self)
        # Alter home page layouts drop-down
        for item in ret:
            if item['name'] == 'ckan.homepage_style':
                item['options'] = [{'value': '1', 'text': _('OGP Home Page')},
                                   {'value': '301', 'text': _('Redirect Home Page to External Site')}]
                break
        # Add input for 301 redirect URL from the home page
        ret.append({'name': 'ckan.abgov_301_url',
                    'control': 'input',
                    'label': _('Home Page URL'),
                    'placeholder': _('Redirect URL')})
        return ret

    def _index_or_redirect(self):
        """ Overide CKAN home controller to allow for home page redirect.
            The redirect happens when home page layout number is set to 301.
            The url is saved by CKAN admin Config Options page (customized above).
        """
        from ckan.lib.app_globals import app_globals
        from pylons.controllers.util import redirect
        if app_globals.homepage_style == '301':
            redirect(app_globals.abgov_301_url, code=301)
        else:
            return _orig_home_index(self)

    # Monkey patch CKAN Admin controller helper
    admin.AdminController._get_config_form_items = _get_config_form_items_patched
    # Monkey patch CKAN home controller
    home.HomeController.index = _index_or_redirect

    # Ensure new key is loaded by CKAN - IConfigurer.update_config_schema was added in 2.4.0
    from ckan.lib.app_globals import auto_update
    auto_update.append('ckan.abgov_301_url')


# Execute the patches
patch_ckan_admin()


class Open_AlbertaPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.interfaces.IActions)
    plugins.implements(plugins.IRoutes, inherit=True)

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'open_alberta')

    def get_helpers(self):
        return {'open_alberta_latest_datasets': latest_datasets,
                'open_alberta_check_archive_date': check_archive_date}

    def get_actions(self):
        # Registers the custom API method defined above
        return {'counter_on': counter_on_off}

    def before_map(self, m):
        m.connect('private-packages' ,'/dashboard/datasets/private',
                  controller='ckanext.open_alberta.controller:DashboardPackagesController',
                  action='dashboard_datasets')
        m.connect('clone', '/dataset/clone/{id}',
                  controller='ckanext.open_alberta.controller:PackageCloneController',
                  action='index')

        m.connect('delete-multiple' ,'/datasets/delete_multiple',
                  controller='ckanext.open_alberta.controller:PackagesDeleteController',
                  action='delete_datasets')
        return m


class DateSearchPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IPackageController, inherit=True)

    def update_config(self, config):
        toolkit.add_template_directory(config, 'templates')
        # toolkit.add_resource('fanstatic', 'ckanext-datesearch')

    def before_search(self, search_params):
        extras = search_params.get('extras')
        if not extras:
            # There are no extras in the search params, so do nothing.
            return search_params
        start_date = extras.get('start_date')
        end_date = extras.get('end_date')
        if not start_date or not end_date:
            # The user didn't select a start and end date, so do nothing.
            return search_params

        # Add a date-range query with the selected start and end dates into the
        # Solr facet queries.
        fq = search_params['fq']
        fq = '{fq} +metadata_created:[{start_date} TO {end_date}]'.format(
            fq=fq, start_date=start_date, end_date=end_date)
        search_params['fq'] = fq
        return search_params

## RSS Feeds Widgets - Places Rss Feed on layout1.html homepage
class RssFeedsWidget(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')

    def get_helpers(self):
        return {
            'rss_fetch_feed': helpers.fetch_feed,
        }

