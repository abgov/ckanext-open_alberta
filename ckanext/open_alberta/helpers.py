from ckan.plugins import toolkit
from ckan.lib import search
from pylons import config
import feedparser
import re
import logging
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

