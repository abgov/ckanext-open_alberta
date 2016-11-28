from dateutil.relativedelta import relativedelta
from pylons import config
from nose.tools import assert_equals, assert_raises
from ckanext.open_alberta.errors import *
from ckanext.open_alberta.controller import ReviewController


class TestReviewController(object):
    def test__review_interval_from_config__no_config_present(self):
        rc = ReviewController()
        assert_raises(ConfigError, rc._review_interval_from_config)

    def test__review_interval_from_config__bad_value(self):
        rc = ReviewController()
        config['open_alberta.review.default_interval'] = 'foobar'
        assert_raises(ConfigError, rc._review_interval_from_config)

    def test__review_interval_from_config__proper_values(self):
        rc = ReviewController()

        # Test proper format with added whitespace
        config['open_alberta.review.default_interval'] = ' 7   days  '
        assert_equals(rc._review_interval_from_config(), {'days': 7})

        config['open_alberta.review.default_interval'] = '1 	week  '
        assert_equals(rc._review_interval_from_config(), {'weeks': 1})

        config['open_alberta.review.default_interval'] = '1 weeks  '
        assert_equals(rc._review_interval_from_config(), {'weeks': 1})

        config['open_alberta.review.default_interval'] = '6 months'
        assert_equals(rc._review_interval_from_config(), {'months': 6})

        # Test if not affected by the case
        config['open_alberta.review.default_interval'] = '6 MONTHS'
        assert_equals(rc._review_interval_from_config(), {'months': 6})

        config['open_alberta.review.default_interval'] = '1 year'
        kwargs = rc._review_interval_from_config()
        assert_equals(relativedelta(years=1), relativedelta(**kwargs))
