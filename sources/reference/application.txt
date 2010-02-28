Application
===========

A Rowan Tree can't directly work with WSGI - it doesn't use a WSGI compliant
API. To connect a WSGI request to a Rowan Tree we use the :class:`Application`
class. 

Applications are fully WSGI compliant, and they hold a single root controller
for the Rowan tree. When requests arrive via WSGI, the application creates a
:class:`~rowan.core.http.HttpRequest`  object, and passes it to the root
controller. It then takes the :class:`~rowan.core.http.HttpResponse` class
that is returned and converts it into the correct WSGI call (i.e. to 
:func:`start_response`).

Applications also have a convenience web-server built in, that can be started
by calling their :meth:`~rowan.core.application.Application.simple_serve` 
method. This is a non-production-safe webserver that uses Python's built
in :func:`wsgiref.simpleserver.makeserver` function.

API
---

.. automodule:: rowan.core.application

.. autoclass:: rowan.core.application.Application
   :members:
   :undoc-members:

