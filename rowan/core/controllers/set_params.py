from __future__ import with_statement
import logging

class SetParams(object):
    """
    A controller that sets parameters in the request.
    """
    logger = logging.getLogger('controller.SetParams')
    
    def __init__(self, controller, **kws):
        self.kws = kws
        self.controller = controller
        
    def __call__(self, request):
        self.logger.debug(
            'Setting parameter(s): %s.' % ', '.join(self.kws.keys())
            )
        with request.set(**self.kws):
            return self.controller(request)
            
    def _get_children(self):
        return [self.controller]
    children = property(_get_children)
    