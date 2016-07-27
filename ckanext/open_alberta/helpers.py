from ckan.plugins import toolkit
from ckan.lib import search
from pylons import config
import feedparser


def fetch_feed(feed_url, number_of_entries=1):
    feed = feedparser.parse(feed_url)
    feed['entries'] = feed['entries'][:number_of_entries]
    return feed

