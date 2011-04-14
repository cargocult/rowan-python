"""
Basic controllers for common use.
"""

from __future__ import with_statement
import logging
import re
import os

import rowan.http as http
import base

class ErrorHandler(base.Wrapper):
    """
    Catches errors and generates a valid error message.

    This responds to error messages by outputting an error page. It is
    given a controller that it will try to call, and will only respond
    if the controller fails to generate a response.

    The error message output by this controller will consist just of a
    page with the HTTP status code on it. In production you'll
    probably want to render more useful and customized error
    messages. You could do that either by subclassing this class, or
    using a :class:`~rowan.controllers.core.Fallback` controller.
    """
    def __init__(self, controller, handle_system_errors=True):
        super(ErrorHandler, self).__init__(controller)
        self.handle_system_errors = handle_system_errors

    def __call__(self, request):
        try:
            return self.controller(request)
        except BaseException, err:
            # Always handle our own errors.
            if isinstance(err, http.HttpError):
                self.get_logger().info("Handling error: %s" % str(err))
                error = err

            # Optionally handle any error.
            elif self.handle_system_errors:
                self.get_logger().info("Handling error: %s" % str(err))
                error = http.Http500(
                    "%s: %s" % (err.__class__.__name__, str(err))
                    )

            # Otherwise raise the error so it appears in stderr.
            else:
                self.get_logger().warning("Ignoring error: %s" % str(err))
                raise

        # Render a simple HTML response.
        msg = "<html><body><h1>%s</h1></body></html>" % \
            error.status_code_string
        return http.HttpResponse(msg, status_code=error.status_code)

class SetParams(base.Wrapper):
    """
    A controller that sets parameters in its subtree.

    When you use this class, you pass in a child controller. This
    controller sets the parameters that need to change in the
    :class:`HttpRequest`, then delegate to the child controller.

    The parameter change is carried out using a `with` statement,
    using the :meth:`~rowan.utils.blackboard.Blackboard.set`
    method of the :class:`Blackboard` class, so the changes are
    reversed before the controller finishes processing, even if an
    error is raised further down the tree.
    """
    def __init__(self, controller, **kws):
        super(SetParams, self).__init__(controller)
        self.kws = kws

    def __call__(self, request):
        self.get_logger().debug(
            'Setting parameter(s): %s.' % ', '.join(self.kws.keys())
            )
        with request.set(**self.kws):
            return self.controller(request)

class Fallback(base.Selector):
    """
    Tries to use a set of controllers in turn.

    The first controller in the given list that succeeds will have its
    response used. If no controllers succeed, then Feedback will raise
    the last error it came across.

    Takes one possible keyword argument 'status_codes'. If given then
    it should be a list of numeric HTTP status codes. This fallback
    will only go through its normal fallback behavior for errors with
    status codes matching those given. Other error codes will be
    reported immediately.  This allows you to build fallbacks that
    only fallback on 404 errors, for example. Note that responses are
    always returned, their status code is never checked.
    """
    logger = logging.getLogger('controller.Fallback')

    def __init__(self, *controllers, **kwargs):
        super(Fallback, self).__init__(*controllers)
        self.status_codes = set(kwargs.get('status_codes', []))

    def __call__(self, request):
        # Try each registered controller in turn.
        for controller in self.controllers:
            try:
                return controller(request)
            except http.HttpError, err:
                self.get_logger().debug("Contoller failed, falling back.")
                if (self.status_codes and
                    err.status_code not in self.status_codes):
                    raise

        # We ran out of options.
        if not err: err = http.Http500("No controllers in Fallback.")
        self.get_logger().debug("No more valid controllers - returning.")
        raise err

class Router(base.BaseController):
    """
    Dispatches requests based on the requested path.

    Routers hold a series of regular expressions that determine which
    controllers are called. Each controller is given as a tuple-pair
    of regular expression and controller.

    Any groups in the regular expression are added to a context
    property called 'router_args', any named groups are placed in a
    property called 'router_kws'. If several routers are found in the
    same branch of the tree, both these properties will grow as new
    groups are found.

    Finally, the path in the request object is rewritten to remove
    everything from the start of the path to the end of the
    match. This means that you can have a router listening for a
    common prefix (such as a section of the site), followed by another
    listening for individual pages within that section, without having
    the section name repeated for each entry in the second router.
    """
    def __init__(self, *mappings):
        self.mappings = [
            (re.compile(re_string), controller)
            for re_string, controller in mappings
            ]
        self.controllers = [controller for regex, controller in mappings]

    def __call__(self, request):
        self.get_logger().debug("Routing path: %s" % request.path)
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
                try:
                    context_update['path_stack'] = \
                        request.path_stack + [request.path]
                except AttributeError:
                    context_update['path_stack'] = [request.path]
                context_update['path'] = request.path[match.end():]

                # Change the context for our children only
                with request.set(**context_update):
                    return controller(request)

        raise http.Http404("No matching URL found.")

    def get_children(self):
        return [self.controllers]


