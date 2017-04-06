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
from ckan.common import _
from ckan.lib.plugins import DefaultGroupForm
import json

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


# Replace Homepage drop-down select contents

import ckan.controllers.admin as admin
import ckan.controllers.home as home
from ckan.lib.app_globals import app_globals

_orig_get_config_form_items = admin.AdminController._get_config_form_items
_orig_home_index = home.HomeController.index

def patch_ckan_admin_and_home_controllers():
    def __patched__get_config_form_items(self):
        ret = _orig_get_config_form_items(self)
        for item in ret:
            if item['name'] == 'ckan.homepage_style':
                item['options'] = [{'value': '1', 'text': _('IDDP home page')},
                                   {'value': '2', 'text': _('OGP home page')},
                                   {'value': '301', 'text': _('Redirect Home Page to External Site')}]
                break
        ret.append({'name': 'ckan.abgov_301_url',
                    'control': 'input',
                    'label': _('Home Page URL'),
                    'placeholder': _('Redirect URL')})
        ret.append({'name': 'ckan.abgov_display_notice',
                    'control': 'checkbox',
                    'value': toolkit.asbool(app_globals.abgov_display_notice),
                    'label': _('Display site notice')})
        ret.append({'name': 'ckan.abgov_notice',
                    'control': 'markdown',
                    'label': _('Site notice'),
                    'placeholder': _('Markdown syntax. Raw HTML is also suppported.')})
        return ret

    def _index_or_redirect(self):
        """ Overide CKAN home controller to allow for home page redirect.
            The redirect happens when home page layout number is set to 301.
            The url is saved by CKAN admin Config Options page (customized above).
        """
        from pylons.controllers.util import redirect
        if app_globals.homepage_style == '301':
            redirect(app_globals.abgov_301_url, code=301)
        else:
            return _orig_home_index(self)

    # Monkey patch CKAN Admin controller helper
    admin.AdminController._get_config_form_items = __patched__get_config_form_items
    # Monkey patch CKAN home controller
    home.HomeController.index = _index_or_redirect


patch_ckan_admin_and_home_controllers()


class Open_AlbertaPlugin(plugins.SingletonPlugin, DefaultGroupForm):
    plugins.implements(plugins.IConfigurable)
    plugins.implements(plugins.IConfigurer, inherit=True)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.interfaces.IActions)
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.IAuthFunctions)
    plugins.implements(plugins.IGroupForm)
    plugins.implements(plugins.IPackageController, inherit=True)


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

    """ IConfigurable """
    def configure(self, config):
        from ckan.controllers.group import GroupController
        # Tell core group controller to handle topics groups
        GroupController.add_group_type('topics')

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

    def update_config_schema(self, schema):
        from ckan.logic.validators import boolean_validator
        schema.update({
            'menu_items': [],
            'ckan.abgov_301_url': [],
            'ckan.abgov_display_notice': [boolean_validator],
            'ckan.abgov_notice': []
        })
        return schema
 
    #ITemplateHelpers
    def get_helpers(self):
        return {
            'open_alberta_latest_datasets': latest_datasets,
            'open_alberta_check_archive_date': check_archive_date,
            'config_datasets_per_pg_options': oab_helpers.items_per_page_from_config,
            'topics': oab_helpers.topics,
            'total_package_count': oab_helpers.total_package_count,
            'menu_items': oab_helpers.menu_items,
            'have_plugin': oab_helpers.have_plugin,
            'is_future_date': oab_helpers.is_future_date,
            'resource_format_to_icon': oab_helpers.resource_format_to_icon,
            'search_facet_items': oab_helpers.search_facet_items,
        }


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

        m.connect('topics', '/topics', controller='group', action='index')

        m.connect('topics_read', '/topics/{id}', controller='group', action='read')

        return m


    # IGroupForm
    def is_fallback(self):
        return False

    def group_types(self):
        return ['topics']

    def index_template(self):
        return 'group/topics.html'

    # IPackageController
    def _update_group_topics(self, ctx, pkg):
        if 'topics' not in pkg:
            return
        del_action = toolkit.get_action('member_delete')
        add_action = toolkit.get_action('member_create')
        all_topics = toolkit.get_action('group_list')(ctx, {'type':'topics', 'all_fields': True})
        topics = json.loads(pkg['topics'])

        for grp in all_topics:
            grp = grp['name']
            if grp in topics:
                add_action(ctx, {'id': grp, 
                                 'object': pkg['id'], 
                                 'object_type': 'package',
                                 'capacity': 'public'})
            else:
                del_action(ctx, {'id': grp, 'object': pkg['id'], 'object_type': 'package'})

    def after_update(self, ctx, pkg):
        """ Update group membership of the dataset that was just saved based on the value of topics field """
        self._update_group_topics(ctx, pkg)
        
    def after_create(self, ctx, pkg):
        """ Update group membership of the dataset that was just saved based on the value of topics field """
        self._update_group_topics(ctx, pkg)

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
        as_funcs['package reviewed'] = lambda *args: _(self._REVIEWED_STR)
        as_icons['package reviewed'] = 'certificate'
        object_id_validators['package reviewed'] = toolkit.get_validator('package_id_exists')

