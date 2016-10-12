# -*- coding: utf-8 -*-
""" Open Alberta CKAN extension """

# Default date format to use: YYYY-MM-DD
DATE_FORMAT = '%Y-%m-%d'

# TODO: remove the commented out code before commiting.

#class CkanApi(object):
#    """
#    A convenience/astethics wrapper for ckan.plugins.toolkit.get_action
#    Allows the user to say
#       CkanApi.package_show(id='some-id', include_tracking=True)
#    instead of
#       toolkit.get_action('package_show')
#           (None, datadict={'id': 'some-id',
#                            'include_tracking': True})
#
#    All APIs returned by toolkit.get_action are supported.
#    The context argument to the action function is usually None 
#    so it was moved to a keyword argument 'context'.
#    """
#    class _CkanApiMethods(type):
#        """ Metaclass to allow dynamic static methods """
#        def __getattr__(cls, attr):
#            def _call(*args, **kwargs):
#                """ get an action from CKAN toolkit and invoke it. """
#                #pylint: disable=unused-argument
#                import ckan.plugins.toolkit as tk
#                ctx = kwargs.pop('context', None)
#                return tk.get_action(attr)(ctx, data_dict=kwargs)
#            setattr(cls, attr, staticmethod(_call))
#            return getattr(cls, attr)
#
#    __metaclass__ = _CkanApiMethods
