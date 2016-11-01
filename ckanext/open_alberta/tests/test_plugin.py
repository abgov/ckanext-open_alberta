"""Tests for plugin.py."""

import ckan.model as model
import ckan.plugins as plugins
import ckan.logic as logic
import ckan.config.middleware
import paste.fixture
import pylons.test
import pylons.config as config
from routes import url_for
import webtest
from nose.tools import (assert_equal, assert_not_equal, assert_raises, assert_true, assert_in)
import ckan.tests.legacy as tests
import ckan.tests.helpers as helpers
import ckan.tests.factories as factories
from pprint import PrettyPrinter
import logging

logger = logging.getLogger('root')

def _get_package_new_page_as_sysadmin(app):
    user = factories.Sysadmin()
    env = {'REMOTE_USER': user['name'].encode('ascii')}
    response = app.get(
        url='/camel-photos/new',
        extra_environ=env,
    )
    return env, response


class TestClonePlugin(helpers.FunctionalTestBase):
    def test_devel(self):
        pp = PrettyPrinter(indent=2)
        app = self._get_test_app()


        #1 create a package
        logger.debug('*************************************************************')

        #url = url_for(controller='package', action='new')
        env, response = _get_package_new_page_as_sysadmin(app)
        form = response.forms['dataset-edit']
        assert_true('humps' in form.fields, msg='!!!!!!!!!!! humps not in form !!!!!!!!!!!')

        with open("/home/vagrant/response.html", "w") as f:
            f.write(resp._body)

        logger.debug('*************************** dataset-edit fields:')
        logger.debug(pp.pformat(form.__dict__))
        form['title'] = 'DS1'
        form['name'] = 'ds1'
        form['notes'] = 'test'
        form['date_created'] = '01/01/2001'
        form['date_modified'] = '01/01/2001'

        resp = helpers.submit_and_follow(self.app, form, env, 'save')
        #pkg = model.Package.by_name('ds1')
        #logger.debug(pp.pformat(pkg))
        
        #2 clone
        # This doesn't work - form expects opendata package
        #resp = app.get(url='/dataset/ds1', extra_environ=env)
        #resp = app.get(url=url_for('clone', id='ds1'), extra_environ=env)
        #assert_true('id-clone-ds-form' in resp, msg='Response did not contain clone form')

        logger.debug('********************* RESPONSE:')
        logger.debug(str(resp))

        logger.debug('*************************************************************')

        assert_true(False, msg='***************** THIS ACTUALLY COMPLETED :O ******************')
