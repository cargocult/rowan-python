"""
Some base classes for common styles of controller.
"""

import logging

class LoggingMixin(object):
    """
    We generally want to be able to log the behavior of
    controllers. This mixin makes a logging object available.
    """
    @classmethod
    def get_logger(cls):
        if not hasattr(cls, "_logger"):
            cls._logger = logging.getLogger("controller.%s" % cls.__name__)
        return cls._logger


class BaseController(LoggingMixin):
    """
    A base class for most types of controller.
    """
    @classmethod
    def import_dependencies(cls):
        """
        This is called only if the wrapper is instantiated. It is used
        so we can define libraries importing dependences that never
        need to be installed if the associated subclasses are not
        instantiated.
        """
        pass

    def __new__(cls, *args, **kws):
        if cls.import_dependencies:
            cls.import_dependencies()
            cls.import_dependencies = None
        instance = super(BaseController, cls).__new__(cls)
        instance.__init__(*args, **kws)
        return instance

    def __call__(self, request):
        raise NotImplementedError(
            "Controllers should implement a __call__ method."
            )

    def get_children(self):
        """
        Base controllers have no children. Single or multiple children
        are managed by `Wrapper` and `Selector` base classes,
        respectively.
        """
        return []

class Wrapper(BaseController):
    """
    A wrapper is a controller with a single child that it may or may
    not choose to call.
    """
    def __init__(self, controller):
        self.controller = controller

    def get_children(self):
        return [self.controller]

class Selector(BaseController):
    """
    A controller base class that manages many children in a list.
    """
    def __init__(self, *controllers):
        self.controllers = controllers

    def get_children(self):
        return self.controllers
