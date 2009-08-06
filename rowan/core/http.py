"""This module contains classes that encapsulate the user's request 
(:class:`HttpRequest`), and either a normal response (:class:`HttpResponse`)
or an error (:class:`HttpError`)."""

from cStringIO import StringIO
import datetime
from cgi import parse_qs, escape

import rowan.core.utils.blackboard as blackboard

HTTP_STATUS_CODES = {
    100: 'CONTINUE',
    101: 'SWITCHING PROTOCOLS',
    200: 'OK',
    201: 'CREATED',
    202: 'ACCEPTED',
    203: 'NON-AUTHORITATIVE INFORMATION',
    204: 'NO CONTENT',
    205: 'RESET CONTENT',
    206: 'PARTIAL CONTENT',
    300: 'MULTIPLE CHOICES',
    301: 'MOVED PERMANENTLY',
    302: 'FOUND',
    303: 'SEE OTHER',
    304: 'NOT MODIFIED',
    305: 'USE PROXY',
    306: 'RESERVED',
    307: 'TEMPORARY REDIRECT',
    400: 'BAD REQUEST',
    401: 'UNAUTHORIZED',
    402: 'PAYMENT REQUIRED',
    403: 'FORBIDDEN',
    404: 'NOT FOUND',
    405: 'METHOD NOT ALLOWED',
    406: 'NOT ACCEPTABLE',
    407: 'PROXY AUTHENTICATION REQUIRED',
    408: 'REQUEST TIMEOUT',
    409: 'CONFLICT',
    410: 'GONE',
    411: 'LENGTH REQUIRED',
    412: 'PRECONDITION FAILED',
    413: 'REQUEST ENTITY TOO LARGE',
    414: 'REQUEST-URI TOO LONG',
    415: 'UNSUPPORTED MEDIA TYPE',
    416: 'REQUESTED RANGE NOT SATISFIABLE',
    417: 'EXPECTATION FAILED',
    500: 'INTERNAL SERVER ERROR',
    501: 'NOT IMPLEMENTED',
    502: 'BAD GATEWAY',
    503: 'SERVICE UNAVAILABLE',
    504: 'GATEWAY TIMEOUT',
    505: 'HTTP VERSION NOT SUPPORTED',
}
"""A dictionary mapping the HTTP response code to a simple human readable
description, in English."""


class HttpRequest(blackboard.Blackboard):
    """Encapsulates data about the request that the user initiated. The
    request contains data such as the  HTTP method, the path requested
    and the IP address of the requesting machine (although this later
    value may be spoofed or mangled by proxies). It also contains
    any additional data that parts of the tree want to set for controllers
    lower down the tree."""
    
    def __init__(self, wsgi_env):
        # Datestamp immediately,
        self.received = datetime.datetime.now()

        # In case we need it, the raw data is stored.
        self.__env = wsgi_env

        # Basic request data.
        self.method = wsgi_env['REQUEST_METHOD']
        self.remote_addr = wsgi_env['REMOTE_ADDR']
        self.path = wsgi_env.get("PATH_INFO", "")
        self.query_raw = wsgi_env.get('QUERY_STRING', '')
        
        # TODO: Do something cleverer with these dictionaries.
        self.body_params = parse_qs(self.body_raw)
        self.query_params = parse_qs(self.query_raw)
        self.all_params = dict()
        self.all_params.update(self.query_params)
        self.all_params.update(self.body_params)
        
    def _get_body_raw(self):
        try:
            return self._body_raw
        except AttributeError:
            # Try to find how much content we were passed.
            try:
                content_length = int(self.__env.get('CONTENT_LENGTH', 0))
            except (ValueError, TypeError):
                content_length = 0
            
            if content_length > 0:
                # Read the input from the designated file-like object and 
                # write it to an output string.
                output_buffer = StringIO()
                input_buffer = self.__env['wsgi.input']
                while content_length > 0:
                    chunk = input_buffer.read(min(16*1024, content_length))
                    if not chunk: break
                    output_buffer.write(chunk)
                    content_length -= len(chunk)
                    
                self._body_raw = output_buffer.getvalue()
                output_buffer.close()
            else:
                # We had no content.
                self._body_raw = ''
                
            return self._body_raw        
    body_raw = property(
        _get_body_raw, 
        doc=("The raw data from the body of the request. This data is "
            "more commonly accessed through the ``body_params`` property, "
            "but in some cases we want the raw input.")
        )
        
class Statused(object):
    """A base class for both kinds of response, normal and exceptional. Both
    need to hold the HTTP status code, so this base class provides that
    functionality."""
    def __init__(self, status_code):
        self.status_code = status_code

    def _get_status_code_string(self):
        return "%d %s" % (
            self.status_code, HTTP_STATUS_CODES[self.status_code]
            )
    status_code_string = property(
        _get_status_code_string, 
        doc="Human-readable text corresponding to the current status code."
        )
        
class HttpResponse(Statused):
    """
    A response generated from a controller indicating that the 
    request was correctly handled and a response should be returned to the
    user. Instances of this class should be returned from every controller,
    controllers may also terminate by raising a :class:`HttpError` instnce.
    """
    def __init__(self, content, content_type='text/html', status_code=200):
        Statused.__init__(self, status_code)
        self.content_type = content_type
        self.content = content        
        
    def _get_headers(self):
        return [('Content-type', self.content_type)]
    headers = property(
        _get_headers, 
        doc=("Gets the headers for this request, to return as part of the "
             "HTTP response. This property is read-only and intended for "
             "internal use.")
        )
    
class HttpError(Exception, Statused):
    """
    An error raised by a controller to indicate that it was not able 
    to process the request through to completion.
    """
    
    def __init__(self, message="", status_code=500):
        """
        Arguments:
        
        ``message``
            A message describing what went wrong. This should be different
            and more specific than the HTTP-code message (e.g. File not Found).
            Or else it should be left blank.
            
        ``status_code``
            The status code that should be associated with this error. If the
            error gets all the way back to the user, this will control the 
            HTTP response code.
        """
        Exception.__init__(self, message)
        Statused.__init__(self, status_code)
        
class Http404(HttpError): 
    """
    A :class:`HttpError` subclass for page-not-found errors.
    """
    def __init__(self, message=""):
        super(Http404, self).__init__(message, 404)
        
class Http500(HttpError): 
    """
    A :class:`HttpError` subclass for general server errors.
    """
    def __init__(self, message=""):
        super(Http500, self).__init__(message, 500)
