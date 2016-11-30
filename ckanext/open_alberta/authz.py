import ckan.authz as authz
import ckan.lib.helpers as h


def is_authorized(action, context, data_dict=None):
    if context.get('ignore_auth'):
        return {'success': True}

    auth_function = authz._AuthFunctions.get(action)
    if auth_function:
        username = context.get('user')
        user = authz._get_user(username)

        if user:
            # deleted users are always unauthorized
            if user.is_deleted():
                return {'success': False}
            # sysadmins can do anything unless the auth_sysadmins_check
            # decorator was used in which case they are treated like all other
            # users.
            elif user.sysadmin:
                if not getattr(auth_function, 'auth_sysadmins_check', False):
                    return {'success': True}

        # If the auth function is flagged as not allowing anonymous access,
        # and an existing user object is not provided in the context, deny
        # access straight away
        if not getattr(auth_function, 'auth_allow_anonymous_access', False) \
           and not context.get('auth_user_obj'):
            """
            return {'success': False,
                    'msg': '{0} requires an authenticated user'
                            .format(auth_function)
                   }
            """
            """
            Here we do not want to show not authorized. we want to
            rediret to login url
            """
            return h.redirect_to("/user/login?came_from={0}".format(h.full_current_url()))
            

        return auth_function(context, data_dict)
    else:
        raise ValueError(_('Authorization function not found: %s' % action))