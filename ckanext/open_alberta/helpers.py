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
