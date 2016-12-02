from ckan.plugins import toolkit
from ckan.lib import search
from ckan.common import g
from pylons import config
import feedparser
import re
import logging
import json
from errors import ConfigError
from datetime import date
from dateutil import parser


def fetch_feed(feed_url, number_of_entries=1):
    feed = feedparser.parse(feed_url)
    feed['entries'] = feed['entries'][:number_of_entries]
    return feed


DEFAULT_DATASETS_PER_PAGE_OPTIONS = '10 25 50'


def items_per_page_from_config():
    """ Parse open_alberta.datasets_per_page_options from the config file and return a tuple
        with the values. The values then can be used to initialize a dropdown.
    """
    cfgval = config.get('open_alberta.datasets_per_page_options',
                        DEFAULT_DATASETS_PER_PAGE_OPTIONS)
    values = re.split(r'\s+', cfgval.strip())
    for val in values:
        try:
            dummy = int(val)
            if dummy <= 0:
                raise ConfigError('Invalid value of open_alberta.datasets_per_page_options')
        except ValueError:
            log = logging.getLogger(__name__)
            log.fatal('Invalid value of ckanext.open_alberta.datasets_per_page_options: %s.' +
                      'A space separated list of natural numbers expected.',
                      cfgval)
            raise ConfigError('Invalid value of open_alberta.datasets_per_page_options')
    return values


def is_future_date(strdt):
    """ Check if the passed string represents a future date.
        Empty or invalid input results in False being returned. """
    try:
        dt = parser.parse(strdt).date()
        return dt > date.today()
    except (ValueError, AttributeError):
        return False


def latest_datasets():
    '''Return latest datasets.'''

    datasets = toolkit.get_action('package_search')(
        data_dict={'rows': 4, 'sort': 'metadata_created desc' })

    return datasets['results']


def topics(max=-1):
    search = toolkit.get_action('group_list')
    results = search(data_dict={'sort': 'package_count desc',
                                'type': 'topics',
                                'all_fields': True})
    return results[:max] if max > 0 else results


def total_package_count():
    search = toolkit.get_action('package_search')
    results = search(data_dict={'rows':1, 'start':0})
    count = results['count']
    if count > 100:
        locale.setlocale(locale.LC_ALL, 'en_US')
        # round down to hundreds and use thousand separator
        return 'over ' + locale.format('%d', count / 100 * 100, grouping=True)
    return count


def menu_items():
    return json.loads(g.menu_items)


def have_plugin(name):
    from ckan.plugins.core import plugin_loaded
    return plugin_loaded(name)

