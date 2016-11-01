from ckan.plugins import toolkit
from ckan.lib import search
from pylons import config
import feedparser
from datetime import date
from dateutil import parser

def fetch_feed(feed_url, number_of_entries=1):
    feed = feedparser.parse(feed_url)
    feed['entries'] = feed['entries'][:number_of_entries]
    return feed

def is_future_date(strdt):
    """ Check if the passed string represents a future date.
        Empty or invalid input results in False being returned. """
    try:
        dt = parser.parse(strdt).date()
        return dt > date.today()
    except (ValueError, AttributeError):
        return False

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

