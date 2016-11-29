# encoding: utf-8
from ckan.common import request
import json

CONTENT_TYPES = {
    'text': 'text/plain;charset=utf-8',
    'html': 'text/html;charset=utf-8',
    'json': 'application/json;charset=utf-8',
    'octet-stream': 'application/octet-stream;charset=utf-8',
}


def _finish_ok(self, response_data=None,
               content_type='json',
               resource_location=None):
    '''If a controller method has completed successfully then
    calling this method will prepare the response.
    @param resource_location - specify this if a new
       resource has just been created.
    @return response message - return this value from the controller
                               method
                               e.g. return self._finish_ok(pkg_dict)
    '''
    if resource_location:
        status_int = 201
        self._set_response_header('Location', resource_location)
    else:
        status_int = 200

    if request.params.get('download'):
    	content_type='octet-stream'
    
    return json.dumps(self._finish(status_int, response_data, content_type), indent=2)