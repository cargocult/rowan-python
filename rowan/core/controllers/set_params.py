from __future__ import with_statement
import logging

class SetParams(object):
    """
    A controller that sets parameters in its subtree.
    
    When you use this class, you pass in a child controller. This controller
    sets the parameters that need to change in the :class:`HttpRequest`, then
    delegate to the child controller. 
    
    The parameter change is carried out using a `with` statement, using
    the :meth:`~rowan.core.utils.blackboard.Blackboard.set` method of the
    :class:`Blackboard` class, so the changes are reversed before the
    controller finishes processing, even if an error is raised further 
    down the tree.
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
    children = property(
        _get_children,
        doc="A list containing the controller that is delegated to."
        )
    