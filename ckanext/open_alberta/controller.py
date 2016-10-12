import logging
import re
import urlparse
import requests
from pylons import config
import ckan.logic as logic
import ckan.logic.schema as schema
import ckan.lib.base as base
import ckan.lib.helpers as h
import ckan.lib.navl.dictization_functions as dictization_functions
import ckan.lib.mailer as mailer
import ckan.lib.captcha as captcha
import ckan.plugins.toolkit as toolkit
from ckan.common import _, request, c
from ckan.controllers.user import UserController
from ckanext.open_alberta import DATE_FORMAT
from ckanext.open_alberta.errors import *

unflatten = dictization_functions.unflatten

logger = logging.getLogger(__name__)


class AuthMixin(object):
    """ Access check base class.
    """
    _NOT_AUTHORIZED_MSG = 'Not authorized to see this page'

    def check_access(self, perm, **kwargs):
        """ Usage: check_access('site_read')
                   check_access('package_create', error_msg='Go away')
            Side effect: the context is saved in self._context for subsequent use.
            Keyword args except error_msg are copied to _context.
        """
        self._context = dict(model=base.model,
                             user=base.c.user,
                             auth_user_obj=base.c.userobj)
        errormsg = _(kwargs.pop('error_msg') if 'error_msg' in kwargs else AuthMixin._NOT_AUTHORIZED_MSG)
        #self._context.update(kwargs)
        try:
            toolkit.check_access(perm, self._context, kwargs)
        except logic.NotAuthorized:
            base.abort(401, error_msg)

 
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


class DashboardPackagesController(UserController):
    """This is used to list only user's private data sets"""

    def __before__(self, action, **env):
        UserController.__before__(self, action, **env)
        c.display_private_only = True


class ReviewController(base.BaseController, AuthMixin):
    _DATASET_NOT_FOUND_MSG = 'Dataset not found'

    def __before__(self, action, **env):
        base.BaseController.__before__(self, action, **env)

    def mark_reviewed(self, id):
        """ This is called when the user clicks 'Marked as Reviewed' on a package.
        """
        from datetime import date
        from dateutil.relativedelta import relativedelta

        from pprint import PrettyPrinter
        pp = PrettyPrinter()

        #if toolkit.request.method == 'POST':
        if toolkit.request.method == 'GET':
            package_show = toolkit.get_action('package_show')
            try:
                pkg = package_show(None, {'id': id})
                self.check_access('package_update', id=id)
                # pkg['organization'] from solr does not contain custom data - needs to be read separately
                organization_show = toolkit.get_action('organization_show')
                org = organization_show(None, {'id': pkg['organization']['name'],
                                               'include_datasets': False,
                                               'include_users': False,
                                               'include_groups': False,
                                               'include_tags': False})
                # The interval from config is used if the organization doesn't have that defined
                rtd_kwargs = self._review_interval_from_config()

                if org.get('review_interval', None):
                    rtd_kwargs = {org['review_interval_type'] : int(org['review_interval'])}

                nrdt = date.today() + relativedelta(**rtd_kwargs)
                logger.debug('relativetimedelta kwargs: %s, Package NRD: %s, Original NRD: %s', 
                             rtd_kwargs, nrdt, pkg.get('next_review_date', 'empty'))
                pkg['next_review_date'] = nrdt.strftime(DATE_FORMAT)
                create_activity = toolkit.get_action('activity_create')
                ctx = { 'ignore_auth': True }
                data = {'user_id': base.c.user,
                        'object_id': pkg['id'],
                        'activity_type': 'package reviewed',
                        'data': {'dataset': pkg}}
                act = create_activity(ctx, data)

                package_update = toolkit.get_action('package_update')
                package_update(None, pkg)
            except toolkit.ObjectNotFound:
                base.abort(404, _(self._DATASET_NOT_FOUND_MSG))
            except ConfigError as e:
                logger.fatal('CONFIGURATION ERROR: %s!', e)
                base.abort(500, _(e))
        else:
            toolkit.abort(403, _(self._NOT_AUTHORIZED_MSG))

    def _review_interval_from_config(self):
        """ Reads default review interval from the config.
            Raises a ConfigError if the config value is missing or the value is incorrect.
            Returns: a dictionary with the interval value that dateutil.relativedelta understands.
                     (i.e. {days|weeks|months|years: value}"""

        try:
            review_interval = config['open_alberta.review.default_interval']
            res = re.match(r'^\s*(\d+)\s+(days*|weeks*|months*|years*)\s*$', review_interval, re.IGNORECASE)
            if res:
                key = res.group(2).lower()
                if key[-1] != 's':
                    key += 's'
                return {key : int(res.group(1))}
            else:
                raise ConfigError('Invalid value under open_alberta.review.default_interval key')
        except KeyError:
            raise ConfigError('open_alberta.review.default_interval is missing from config')
        
