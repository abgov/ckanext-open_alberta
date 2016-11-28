from pylons import config
from nose.tools import assert_equals, assert_raises
from helpers import items_per_page_from_config
from errors import ConfigError


class TestHelpers(object):
    def test__items_per_page_from_config__no_config(self):
        if 'open_alberta.datasets_per_page_options' in config:
            del config['open_alberta.datasets_per_page_options']
        assert_equals(items_per_page_from_config(), ['10', '25', '50'])

    def test__items_per_page_from_config__valid_value(self):
        config['open_alberta.datasets_per_page_options'] = '10 25 50'
        assert_equals(items_per_page_from_config(), ['10', '25', '50'])

        config['open_alberta.datasets_per_page_options'] = '  10    25      50   '
        assert_equals(items_per_page_from_config(), ['10', '25', '50'])

        config['open_alberta.datasets_per_page_options'] = ' 1 2  3    4   5 '
        assert_equals(items_per_page_from_config(), ['1', '2', '3', '4', '5'])

    def test__items_per_page_from_config__no_value(self):
        config['open_alberta.datasets_per_page_options'] = ''
        assert_raises(ConfigError, items_per_page_from_config)

    def test__items_per_page_from_config__bad_value(self):
        config['open_alberta.datasets_per_page_options'] = 'qwpoqpweof qpowij wfoij qwoijf woiqjf'
        assert_raises(ConfigError, items_per_page_from_config)

        config['open_alberta.datasets_per_page_options'] = '-5'
        assert_raises(ConfigError, items_per_page_from_config)

        config['open_alberta.datasets_per_page_options'] = '10 0 20'
        assert_raises(ConfigError, items_per_page_from_config)

