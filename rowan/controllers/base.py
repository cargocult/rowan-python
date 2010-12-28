"""
Some base classes for common styles of controller.
"""

import logging

class LoggingController(object):
    """
    We generally want to be able to log the behavior of
    controllers. This mixin/base class makes a logging object
    available.
    """
    @classmethod
    def get_logger(cls):
        if not hasattr(cls, "_logger"):
            cls._logger = logging.getLogger("controller.%s" % cls.__name__)
        return cls._logger

class Wrapper(LoggingController):
    """
    A wrapper is a controller with a single child that it may or may
    not choose to call.
    """
    def __init__(self, controller):
        self.controller = controller

    def get_children(self):
        return [self.controller]

class Chooser(LoggingController):
    """
    A controller base class that manages many children in a list.
    """
    def __init__(self, *controllers):
        self.controllers = controllers

    def get_children(self):
        return self.controllers
