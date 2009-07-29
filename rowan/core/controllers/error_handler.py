import logging

import rowan.core.http as http

class ErrorHandler(object):
    """
    Catches errors and generates a valid error message.
    
    This responds to error messages by outputting an error
    page. It is given a controller that it will try to call, and will only
    respond if the controller fails to generate a response. 
    
    The error message output by this controller will consist just of a page 
    with the HTTP status code on it. In production you'll probably want to 
    render more useful and customized error messages. You could do that 
    either by subclassing this class, or using a 
    :class:`~rowan.core.controllers.Fallback` controller.
    """    
    logger = logging.getLogger('controller.ErrorHandler')
    
    def __init__(self, controller):
        self.controller = controller
        
    def __call__(self, request):
        try:
            return self.controller(request)
        except BaseException, err:
            self.logger.debug("Handling error: %s" % str(err))
            if isinstance(err, http.HttpError):
                error = err
            else:
                error = http.Http500(
                    "%s: %s" % (err.__class__.__name__, str(err))
                    )
        
        # Render a simple HTML response.        
        return http.HttpResponse(
            "<html><body><h1>%s</h1></body></html>" % error.status_code_string,
            status_code=error.status_code
            )

    def _get_children(self):
        return [self.controller]
    children = property(
        _get_children,
        doc="A list containing this controller's child controller."
        )