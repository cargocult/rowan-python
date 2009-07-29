import logging

import rowan.core.http as http

class Fallback(object):
    """
    Tries to use a set of controllers in turn.
    
    The first controller in the given list that succeeds will have
    its response used. If no controllers succeed, then Feedback will
    raise the last error it came across. 
    
    Takes one possible keyword argument 'status_codes'. If given then
    it should be a list of numeric HTTP status codes. This fallback will only 
    go through its normal fallback behavior for errors with status codes 
    matching those given. Other error codes will be reported immediately.
    This allows you to build fallbacks that only fallback on 404 errors,
    for example. Note that responses are always returned, their status code
    is never checked.
    """
    logger = logging.getLogger('controller.Fallback')
    
    def __init__(self, *controllers, **kwargs):
        self.controllers = controllers
        self.status_codes = set(kwargs.get('status_codes', []))
        
    def __call__(self, request):
        # Try each registered controller in turn.
        for controller in self.controllers:
            try:
                return controller(request)
            except http.HttpError, err:
                self.logger.debug("Contoller failed, falling back.")
                if (self.status_codes and 
                    err.status_code not in self.status_codes):
                    raise
                    
        # We ran out of options.
        if not err: err = http.Http500("No controllers in Fallback.")
        self.logger.debug("No more valid controllers - returning.")
        raise err

    def _get_children(self):
        return self.controllers
    children = property(
        _get_children,
        doc="A list of the controllers registered with this router."
        )