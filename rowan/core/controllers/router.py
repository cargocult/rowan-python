"""
This module defines a controller to map URLs to other controllers using 
regular expressions.
"""

from __future__ import with_statement
import logging
import re

import rowan.core.http as http

class Router(object):
    """
    Dispatches requests based on the requested path.
    
    Routers hold a series of regular expressions that determine
    which controllers are called. Each controller is given as a tuple-pair
    of regular expression and controller.
    """
    logger = logging.getLogger('controller.Router')
    
    def __init__(self, *mappings):
        self.mappings = [
            (re.compile(re_string), controller)
            for re_string, controller in mappings
            ]
        self.controllers = mappings.values()
        
    def __call__(self, request):
        self.logger.debug("Routing path: %s" % request.path)
        for regex, controller in self.mappings:
            match = regex.match(request.path)
            if match is not None:
                # Find the match parameters and update the request
                args = match.groups()
                kws = match.groupdict()
                if not hasattr(request, 'router_args'):
                    request.router_args = args
                else:
                    request.router_args += args
                if not hasattr(request, 'router_kws'):
                    request.router_kws = kws
                else:
                    request.router_kws.update(kws)
                
                # Update the path for our children only
                with request.set(path=request.path[match.end():]):
                    return controller(request)
                    
        raise http.Http404("No matching URL found.")

    def _get_children(self):
        return [self.controllers]
    children = property(
        _get_children, 
        doc="A list of the controllers registered with this router."
        )