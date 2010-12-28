"""
Controllers form the basic structure of the framework. They are composed
into trees to build up functionality. Controllers are simply callables that
take only a http.HttpRequest object as input, and either return a HttpResponse
instance containing the result of the request, or raise a HttpError instance
indicating that something went wrong.

This package contains a range of basic controllers.
"""

from core import *
from middleware import *
from content import *
