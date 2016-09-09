import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckanext.open_alberta import helpers
import pylons.config as config
import datetime
from dateutil.parser import parse


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

        m.connect('private-packages' ,'/dashboard/datasets/private',
                  controller='ckanext.open_alberta.controller:DashboardPackagesController',
                  action='dashboard_datasets')

        m.connect('delete-multiple' ,'/datasets/delete_multiple',
                  controller='ckanext.open_alberta.controller:PackagesDeleteController',
                  action='delete_datasets')

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
    plugins.implements(plugins.IPackageController, inherit=True)

    #IPackageController
    def before_view(self, pkg_dict):
        """ check the published date. If it is after current date,
            the private field will be checked and turn to public if
            it is private, and update dataset in database. 
            If before or equal to current date, the private field 
            will not bed checked. If published date field is empty, 
            no check on private field.
        """ 
        if not pkg_dict.get('date_published'):
            return pkg_dict

        date_published = parse(pkg_dict['date_published'])
        today = datetime.datetime.now()
        if today < date_published:
            """date_published is later than today"""
            return pkg_dict
        else:
            if pkg_dict['private'] == False: #public
                return pkg_dict
            else: # private
                pkg_dict['private'] = False
                pkg_dict['state'] = 'active'
                datasets = toolkit.get_action('package_update')(
                            data_dict=pkg_dict)
        return pkg_dict

    #IConfigurer
    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'open_alberta')
    
    #ITemplateHelpers
    def get_helpers(self):
        return {'open_alberta_latest_datasets': latest_datasets}

    #IActions
    def get_actions(self):
        # Registers the custom API method defined above
        return {'counter_on': counter_on_off}

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

