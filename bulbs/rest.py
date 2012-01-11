# -*- coding: utf-8 -*-
#
# Copyright 2011 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#
"""
Low-level module for connecting to the Rexster REST server and
returning a Response object.

"""

import logging
log = logging.getLogger(__name__)

import urllib
import httplib2
import ujson as json
from pprint import pprint

from resource import Response

def get_error(http_resp):
    """Returns the HTTP status, message, and error."""
    header, content = http_resp
    content = json.loads(content)
    status = header.get('status')
    message = content.get('message')
    error = content.get('error')
    return status, message, error 

def print_error(http_resp):
    """Pretty prints the error."""
    status, message, error = get_error(http_resp)
    pprint(error)

# HTTP Response Handlers
def ok(http_resp):
    return

def created(http_resp):
    return
    
def no_content(http_resp):
    return

def bad_request(http_resp):
    raise ValueError(http_resp)

def not_found(http_resp):
    raise LookupError(http_resp)
    #return None

def conflict(http_resp):
    raise SystemError(http_resp)

def server_error(http_resp):
    raise SystemError(http_resp)

RESPONSE_HANDLERS = {200:ok,
                     201:created,
                     204:no_content,
                     400:bad_request,
                     404:not_found,
                     409:conflict,
                     500:server_error}

class Request(object):
    """Used for connecting to the Rexster REST server."""

    response_class = Response

    def __init__(self, config, content_type):
        """
        Initializes a resource object.

        :param root_uri: the base URL of Rexster.

        """
        self.config = config
        self.content_type = content_type
        self.http = httplib2.Http()    
        self._add_credentials(config.username, config.password)
    
    def get(self, path, params=None):
        """Convenience method that sends GET requests to the resource.""" 
        return self.request("GET", path, params)

    def put(self, path, params=None):
        """Convenience method that sends PUT requests to the resource."""
        return self.request("PUT", path, params)

    def post(self, path, params=None):
        """Convenience method that sends POST requests to the resource."""
        return self.request("POST", path, params)

    def delete(self, path, params=None):
        """Convenience method that sends DELETE requests to the resource."""
        return self.request("DELETE", path, params)
    
    def request(self, method, path, params):
        """
        Sends a request to the resource.

        :param method: either GET, POST, or DELETE.
        :param target: the URL path relative to the database URL you specified 
                       in either config.py or that you passed in as an argument
                       when you instantiated the resource.
        :param params: a dict of query-string parameters to include in the URL 
        """

        uri, method, body, headers = self._build_request_args(path,method,params)

        self._display_debug(uri,method,body,headers)
       
         # "retry code" moved to _retry_request method for now. - James  
        http_resp = self.http.request(uri, method, body, headers)

        #print http_resp
        return self.response_class(http_resp)

    def _display_debug(self,uri,method,body,headers):
        log.debug("%s url:  %s", method, uri)
        log.debug("%s body: %s", method, body)        

    def _build_request_args(self, path, method, params):
        headers = {'Accept': 'application/json'}
        body = None

        uri = "%s/%s" % (self.config.root_uri.rstrip("/"), path.lstrip("/"))

        if params and method is "GET":
            uri = "%s?%s" % (uri, urllib.urlencode(params))
        
        if params and (method in ["PUT", "POST", "DELETE"]):
            body = json.dumps(params)
            post_headers = {'Content-Type': self.content_type}
            headers.update(post_headers)
        
        return uri, method, body, headers 

    def _add_credentials(self, username, password):
        if username and password:
            self.http.add_credentials(username, password)

