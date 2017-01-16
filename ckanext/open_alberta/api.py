# encoding: utf-8
from ckan.common import request, response
import json

CONTENT_TYPES = {
    'text': 'text/plain;charset=utf-8',
    'html': 'text/html;charset=utf-8',
    'json': 'application/json;charset=utf-8',
    'octet-stream': 'application/octet-stream;charset=utf-8',
}


def download(fn):
    def decorate_finish_ok(self, response_data=None,
                   content_type='json',
                   resource_location=None):
        '''This function is based on the core function plus extras.
           It checks param id to get the id of package and param
           download. If true, it will change the header for download
           type.
        @param resource_location - specify this if a new
           resource has just been created.
        @return response message - return this value from the controller
                                   method
                                   e.g. return self._finish_ok(pkg_dict)
        '''
        if request.params.get('download'):
            content_type='octet-stream'
            if request.params.get('id'):
                id = request.params.get('id')
                response.headers['Content-Disposition'] = "attachment; filename={0}.txt".format(id)
            elif not response.headers.has_key('Content-Disposition'):
                response.headers['Content-Disposition'] = "attachment; filename=none.txt"
            if not isinstance(response_data, str):
                response_data = json.dumps(response_data, indent=2)
        return fn(self, response_data, content_type, resource_location)

    return decorate_finish_ok