import logging
import re
from datetime import datetime
import urlparse
import requests
import ckan.logic as logic
import ckan.lib.base as base
import ckan.plugins.toolkit as toolkit

from ckan.common import _, request, c
import ckan.lib.helpers as h
import ckan.logic as logic
import ckan.logic.schema as schema
import ckan.lib.navl.dictization_functions as dictization_functions
import ckan.lib.mailer as mailer
from ckan.controllers.user import UserController
from ckan.lib.base import BaseController

from pylons import config
from pylons.decorators import jsonify
import ckan.lib.captcha as captcha
from ckan.lib.render import TemplateNotFound

import model

unflatten = dictization_functions.unflatten

_NOT_AUTHORIZED = _('Not authorized to see this page')
_UNEXPECTED_ERROR = _('Server error. Please contact technical support.')


class SuggestController(base.BaseController):

    def __before__(self, action, **env):
        base.BaseController.__before__(self, action, **env)
        try:
            context = {'model': base.model, 'user': base.c.user or base.c.author,
                       'auth_user_obj': base.c.userobj}
            logic.check_access('site_read', context)
        except logic.NotAuthorized:
            base.abort(401, _('Not authorized to see this page'))


    def _send_suggestion(self, context):
        try:
            data_dict = logic.clean_dict(unflatten(
                logic.tuplize_dict(logic.parse_params(request.params))))
            context['message'] = data_dict.get('log_message', '')

            c.form = data_dict['name']
            captcha.check_recaptcha(request)

            #return base.render('suggest/form.html')
        except logic.NotAuthorized:
            base.abort(401, _('Not authorized to see this page'))

        except captcha.CaptchaError:
            error_msg = _(u'Bad Captcha. Please try again.')
            h.flash_error(error_msg)
            return self.suggest_form(data_dict) 


        errors = {}
        error_summary = {}

        if (data_dict["email"] == ''):

            errors['email'] = [u'Missing Value']
            error_summary['email'] =  u'Missing value'

        if (data_dict["name"] == ''):

            errors['name'] = [u'Missing Value']
            error_summary['name'] =  u'Missing value'

        if (data_dict["summary"] == ''):

            errors['summary'] = [u'Missing Value']
            error_summary['summary'] =  u'Missing value'

        if (data_dict["description"] == ''):

            errors['description'] = [u'Missing Value']
            error_summary['description'] =  u'Missing value'


        if len(errors) > 0:
            return self.suggest_form(data_dict, errors, error_summary)
        else:
            # #1799 User has managed to register whilst logged in - warn user
            # they are not re-logged in as new user.
            mail_to = config.get('contact_email_to')
            recipient_name = 'OGP Team'
            subject = 'OGPSuggest - %s' % (data_dict["summary"])

            body = 'Submitted by %s (%s)\n' % (data_dict["name"], data_dict["email"])

            if (data_dict["summary"] != ''):
                body += 'Summary: %s \n' % data_dict["summary"]

            body += 'Request: %s' % data_dict["description"]

            try:
                mailer.mail_recipient(recipient_name, mail_to,
                        subject, body)
            except mailer.MailerException:
                raise


            return base.render('suggest/suggest_success.html')


    def suggest_form(self, data=None, errors=None, error_summary=None):
        suggest_new_form = 'suggest/suggest_form.html'

        context = {'model': base.model, 'session': base.model.Session,
                   'user': base.c.user or base.c.author,
                   'save': 'save' in request.params,
                   'for_view': True}

        if (context['save']) and not data:
            return self._send_suggestion(context)

        data = data or {}
        errors = errors or {}
        error_summary = error_summary or {}
        vars = {'data': data, 'errors': errors, 'error_summary': error_summary}            

        c.form = base.render(suggest_new_form, extra_vars=vars)

        return base.render('suggest/form.html')

    def contact_form(self, data=None, errors=None, error_summary=None):
        contact_new_form = 'suggest/contact_form.html'

        context = {'model': base.model, 'session': base.model.Session,
                   'user': base.c.user or base.c.author,
                   'save': 'save' in request.params,
                   'for_view': True}

        if (context['save']) and not data:
            return self._send_suggestion(context)

        data = data or {}
        errors = errors or {}
        error_summary = error_summary or {}
        vars = {'data': data, 'errors': errors, 'error_summary': error_summary}

        c.form = base.render(contact_new_form, extra_vars=vars)

        return base.render('suggest/form.html')


class PagesController(base.BaseController):

    def __before__(self, action, **env):
        base.BaseController.__before__(self, action, **env)
        try:
            context = {'model': base.model, 'user': base.c.user or base.c.author,
                       'auth_user_obj': base.c.userobj}
            logic.check_access('site_read', context)
        except logic.NotAuthorized:
            base.abort(401, _('Not authorized to see this page'))


    def policy(self):
        return base.render('static-pages/policy/read.html')

    def licence(self):
        return base.render('static-pages/licence/read.html')

    def faq(self):
        return base.render('static-pages/faq/read.html')

    def static_serve(self, slug=None):
        if slug is None:
            return base.render('static-pages/interact.html')
        else:
            try:
                return base.render('static-pages/%s.html' % (slug,))
            except TemplateNotFound:
                base.abort(404);


class DashboardPackagesController(UserController):
    """This is used to list only user's private data sets"""

    def __before__(self, action, **env):
        UserController.__before__(self, action, **env)
        c.display_private_only = True


class PackageCloneController(BaseController):
    """ Controller to faciliatate cloning a package to ease up creating new
        data sets.
    """

    def __before__(self, action, **env):
        """ Checks if the invoking user has permissions to create data sets.
            If the permission check fails, HTTP 401 error is raised.
        """
        base.BaseController.__before__(self, action, **env)
        self._context = dict(model=base.model,
                             user=base.c.user,
                             auth_user_obj=base.c.userobj)
        try:
            logic.check_access('package_create', self._context)
        except logic.NotAuthorized:
            base.abort(401, _NOT_AUTHORIZED)


    @jsonify
    def index(self, id):
        """ Clone the specified data set record.
            Arguments:
              id (string): URL/slug of the data set.
            Returns:
              string: JSON response.
              Successful clone return value: 
                  {'status': 'success', 
                   'redirect_url': <URL of data set edit page>
                  }
              Data validation error return value:
                  {'status': 'error',
                   'errors': {<field1>: [<validation error message>],
                              <field2>: [<validation error message>]}
                  }
              Any other (unexpected) error:
                  {'status': 'error',
                   'errorMessage': <message>
                  }
        """
        logger = logging.getLogger(__name__)

        if toolkit.request.method == 'POST':
            try:
                # TODO: handle publication
                pkg = toolkit.get_action('package_show')(None, dict(id=id))

                cfg_adst = config.get('ckanext.openalberta.clonable_ds_types', 'opendata,publication')
                allowed_types = set(re.split('\s*,\s*', cfg_adst))
                if pkg['type'] not in allowed_types:
                    logger.warn('Requested cloning of unsupported package type (%s). Supported types: %s.',
                                pkg['type'], cfg_adt)
                    return {
                        'status': 'error',
                        'errorMessage': _('This package type is not allowed to be cloned.')
                    }

                pkg['title'] = toolkit.request.params.getone('title')
                pkg['name'] = toolkit.request.params.getone('name')
                pkg['date_created'] = pkg['date_modified'] = datetime.now()
                pkg['state'] = 'draft'
                del pkg['id']

                action = toolkit.get_action('package_create')
                newpkg = action(self._context, pkg)
                return {
                    'status': 'success',
                    'redirect_url': h.url_for(controller='package', action='edit', id=newpkg['name'])
                }
            except toolkit.ValidationError as ve:
                errflds = set(ve.error_dict.keys()) - {'title', 'name'}
                if errflds:
                    # There are validation errors other than title and name (slug).
                    # If this happens, it means something is wrong with the package
                    return {
                        'status': 'error',
                        'errorMessage': _('The data set is in an invalid state. Please correct it before trying to clone.')
                    }
                return {
                    'status': 'error',
                    'errors': ve.error_dict
                }
            except:
                logger.exception('Error in PackageCloneController:index')
                return {
                    'status': 'error',
                    'errorMessage': _UNEXPECTED_ERROR
                }

        else:
            toolkit.abort(403, _NOT_AUTHORIZED)

