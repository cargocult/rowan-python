The Rowan Tree
==============


The Contract
************

The tree works because each controller has the same structure, or contract.
Controllers can therefore be reused where ever they are needed in the tree.

Request and Response
--------------------

Each controller is a Python callable that takes a
:class:`~rowan.core.http.HttpRequest` object as an argument, and either returns a
:class:`~rowan.core.http.HttpResponse` object, or raises a
:class:`~rowan.core.http.HttpError`. Returning a response indicates that the
controller has handled the request (even if the response it is returning
represents some problem, such as a 404 page). Raising an error indicates that
something went wrong, but the controller isn't capable of turning it into a
valid response. Normally this bubbles up the tree until a controller is found
that either has some fallback behavior, or else can turn a raised error into an
error message in a regular :class:`HttpResponse`.

Children
--------

The section above describes the complete extent of the contract for leaves in
the tree. Controllers that manage a subtree should also have a :attr:`children`
attribute defined on the callable. This should return a (possibly empty) list
of the controllers it is currently managing. This allows the tree to be
navigated without executing it, and allows special tasks such as diagramming
the tree to be accomplished.

Controllers represented by classes with a :meth:`__call__` method can simply
define a :attr:`children` instance attribute or property. Controllers
represented by functions can use Python's ability to have function data, as
follows::

    def view1(request):
        return view2(request)
    view1.children = [view2]

Some controllers may select different children depending on the context, in
this case the :attr:`children` attribute should hold all of the possible
children.

In rarer cases there may be an infinite or undecidable set of children. In this
case the :attr:`children` mechanism breaks down, and should be omitted.

Any controller without a :attr:`children` attribute is considered to be
equivalent to having an attribute containing the empty list. So there's no need
to add the attribute to the tree's leaves.



