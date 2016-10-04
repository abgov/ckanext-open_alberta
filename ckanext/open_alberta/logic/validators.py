from ckan.logic.validators import is_positive_integer
from ckan.logic import _import_module_functions, UnknownValidator, get_action
from ckan.common import _
import ckan.lib.navl.dictization_functions as df
import formencode.validators

Invalid = df.Invalid
_validators_cache = {}



def clear_validators_cache():
    _validators_cache.clear()

def get_validator(validator):
    '''Return a validator function by name.

    :param validator: the name of the validator function to return,
        eg. ``'package_name_exists'``
    :type validator: string

    :raises: :py:exc:`~ckan.plugins.toolkit.UnknownValidator` if the named
        validator is not found

    :returns: the named validator function
    :rtype: ``types.FunctionType``

    '''
    if  not _validators_cache:
        validators = _import_module_functions('ckan.lib.navl.validators')
        _validators_cache.update(validators)
        validators = _import_module_functions('ckan.logic.validators')
        _validators_cache.update(validators)
        validators = _import_module_functions('ckanext.review.validators')
        _validators_cache.update(validators)
        _validators_cache.update({'OneOf': formencode.validators.OneOf})
    try:
        return _validators_cache[validator]
    except KeyError:
        raise UnknownValidator('Validator `%s` does not exist' % validator)

def in_range_date_positive_integer(value, context):
    value = is_positive_integer(value, context)
    if value < 1 or value > 999:
        raise Invalid(_('Must be in range from 1 to 999'))
    return value


