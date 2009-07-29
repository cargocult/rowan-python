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
    
    Any groups in the regular expression are added to a context property 
    called 'router_args', any named groups are placed in a property called 
    'router_kws'. If several routers are found in the same branch of the
    tree, both these properties will grow as new groups are found.
    
    Finally, the path in the request object is rewritten to remove everything
    from the start of the path to the end of the match. This means that
    you can have a router listening for a common prefix (such as a section
    of the site), followed by another listening for individual pages
    within that section, without having the section name repeated for each
    entry in the second router.
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
                context_update = {}
                args = match.groups()
                kws = match.groupdict()
                
                if not hasattr(request, 'router_args'):
                    context_update['router_args'] = args
                else:
                    context_update['router_args'] = request.router_args + args
                if not hasattr(request, 'router_kws'):
                    context_update['router_kws'] = kws
                else:
                    d = dict(**request.router_kws)
                    d.update(kws)
                    context_update['router_kws'] = d
                
                # Update the path
                context_update['path'] = request.path[match.end():]

                # Change the context for our children only
                with request.set(**context_update):
                    return controller(request)
                    
        raise http.Http404("No matching URL found.")

    def _get_children(self):
        return [self.controllers]
    children = property(
        _get_children, 
        doc="A list of the controllers registered with this router."
        )