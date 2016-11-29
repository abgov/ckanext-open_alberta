import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckanext.open_alberta import helpers
import pylons.config as config
import datetime
import dateutil.parser as parser
import ckan
from ckanext.open_alberta import authz
import helpers as oab_helpers
import api
import ckan.controllers.api as ckan_api


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


def package_authentication(context, data_dict=None):
    if context['user']:
        return {'success': True}
    else:
        return {'success': False, 'msg': "Not allowed for no user login"}


class OpenAlbertaPagesPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.IConfigurer, inherit=True)

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


class Open_AlbertaPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.interfaces.IActions)
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.IAuthFunctions)

    """
    Monkey patch the ckan authz. Change the default behavior
    when no user login.
    """
    ckan.authz.is_authorized = authz.is_authorized

    """ 
    Monkey patching here to override 
    the content type for download of package's metadata .
    """
    ckan_api.ApiController._finish_ok = api._finish_ok
    ckan_api.CONTENT_TYPES = api.CONTENT_TYPES

    """ IAuthFunctions """
    def get_auth_functions(self):
        return {'package_list': package_authentication,
                'package_show': package_authentication,
                'package_search': package_authentication }

    #IConfigurer
    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'open_alberta')
    
    #ITemplateHelpers
    def get_helpers(self):
        return {'open_alberta_latest_datasets': latest_datasets,
                'open_alberta_check_archive_date': check_archive_date,
                'config_datasets_per_pg_options': oab_helpers.items_per_page_from_config}


    #IActions
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

    import ckan.controllers.package
    from .controller import PagedPackageController
    ckan.controllers.package.PackageController = PagedPackageController


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


class ReviewPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.IConfigurable)
    plugins.implements(plugins.ITemplateHelpers)

    def before_map(self, m):
        m.connect('review' ,'/dataset/review/{id}',
                  controller='ckanext.open_alberta.controller:ReviewController',
                  action='mark_reviewed')
        return m

    # IConfigurable
    # This is called on CKAN startup and before executing various paster commands
    def configure(self, config):
        self._register_reviewed_activity()

    def get_helpers(self):
        return {'is_future_date': helpers.is_future_date }

    _REVIEWED_STR = "{actor} reviewed dataset {dataset}"

    def _register_reviewed_activity(self):
        """ Add 'package reviewed' activity support by monkey patching CKAN
        """
        from ckan.lib.activity_streams import (activity_stream_string_functions as as_funcs,
                                               activity_stream_string_icons as as_icons)
        from ckan.logic.validators import object_id_validators
        from ckan.common import _
        as_funcs['package reviewed'] = lambda *args: _(self._REVIEWED_STR)
        as_icons['package reviewed'] = 'certificate'
        object_id_validators['package reviewed'] = toolkit.get_validator('package_id_exists')

