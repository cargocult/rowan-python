"""This module contains a WSGI-compliant base class from which a complete
site hangs. The elements of the site itself are made up of controllers."""

import http

class Application(object):
    """Handles the top level logic for running a web application. This is
    normally the object you pass to the server as your WSGI application. It 
    acts as an interface between WSGI's calling API and our internal 
    request/response format. Pass the top level request/response handler
    into the constructor."""
    
    def __init__(self, controller):
        self.controller = controller

    def __call__(self, environ, start_response):
        request = http.HttpRequest(environ)
        response = self.controller(request)
        start_response(response.status_code_string, response.headers)
        return [response.content]

    def simple_serve(self, host='localhost', port=8000):
        """Sets up a development WSGI webserver at the given location, serving
        this application."""
        from wsgiref.simple_server import make_server
        srv = make_server(host, port, self)
        print "Rowan development server is running at http://%s:%d/" % (
            host, port
            )
        print "Quit the server with CONTROL-C"
        srv.serve_forever()

    
