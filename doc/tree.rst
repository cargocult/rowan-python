The Rowan Tree
==============

Controllers in Rowan are composed into a tree. The first controller in
the tree (called the 'root'), is responsible for handling *all*
requests that come in and for generating *all* responses. It is the
central port of call for the framework.

Because you're unlikely to want the same response for all requests,
the root controller will normally keep track of one or more delegate
controllers (normally called its "children"). When a request comes in,
it can decide which of its children should handle the request, and
passes off responsibility to them.

This process can continue to any depth, so controllers can have
children which have children, and so on. In this way the set of
controllers forms a tree, starting at the root and branching as many
times as needed.

Directed Graphs
---------------

Strictly speaking, Rowan controllers are not combined in a tree but in
a rooted directed graph. In a tree, every element has exactly one
parent. In other words it can be reached from only one combination of
branches.

In Rowan one controller can be a child of any number of parents, so it
can be reached from more than one route through the tree.

This is useful because it means that you can have one controller
called with different contexts. You might have a controller that can
output a page with a user's profile on it, for example. It appears in
the tree twice, once associated with a URL which is publically
viewable, and once associated with a URL which is part of the user's
private pages. In the latter case extra controllers in the tree work
out if the user is logged in or not, and set properties in the context
to say who the user is. Then the profile-controller can simply check
these bits of context data and determine how to display itself,
customizing its appearance depending on who is viewing it.

Rowan doesn't prevent you from looping in circles in the tree either
(so one controller is its own ancestor), but this can cause infinite
loops when processing the tree and isn't recommended unless you really
know why you need to do that.


How the Tree is Used
********************

Tree structures are commonly used in algorithms that need to make
decisions. In Artificial Intelligence there are many tree or tree-like
structures: Decision Trees, Behavior Trees, and the Rete algorithm
(for Expert Systems), are a few more common examples.

Rowan uses an algorithm that is based on Behavior Trees. The root
controller of the tree is asked to carry out the whole action. It can
decide to respond, or to delegate to further controllers, and so on
down the tree. If at any point this process can't continue (a leaf
node is reached, but it can't generate a response), then the process
bubbles back up the tree. Some controllers trap this failure and try a
different child, so the process begins to bubble down again. 

In algorithmic terms this is called 'backtracking': trying to find
another way to reach a goal (in this case the goal is to respond
sensibly to the user). Backtracking is a central feature of many AI
algorithms, and is a characteristic of how human beings solve problems
too.




The Contract
************

Rowan allows any combination of controllers to be put together to make
the tree. This works because each controller has the same structure,
or contract. Controllers can therefore be reused where ever they are
needed in the tree [#f1]_.

Request and Response
--------------------

Each controller is a Python callable that takes a
:class:`~rowan.core.http.HttpRequest` object as an argument, and
either returns a :class:`~rowan.core.http.HttpResponse` object, or
raises a :class:`~rowan.core.http.HttpError`. Returning a response
indicates that the controller has handled the request (even if the
response it is returning represents some problem, such as a 404
page)::

    def my_controller(request):
        return http.HttpResponse(content)

Raising an error indicates that something went wrong, but the
controller isn't capable of turning it into a valid response::

    def my_controller(request):
        raise http.HttpError(error_message)

Normally this bubbles up the tree until a controller is found that
either has some fallback behavior, or else can turn a raised error
into an error message in a regular :class:`HttpResponse`.

Because the contract only asks for a python callable it is possible
(and very common) to use a class with a :meth:`__call__` method,
rather than a function::

    class MyController(object):
        def __call__(self, request):
            return http.HttpResponse(content)

Note that there is no common base class to inherit from in this
context, because the only bit of API you need to implement is the
:meth:`__call__` method. Rowan exclusively uses duck typing rather
than type checking.


Children
--------

The previous section describes the complete extent of the contract for
leaves in the tree. Controllers that manage a subtree should also have
a :attr:`children` attribute defined on the callable. This should
return a (possibly empty) list of the controllers it is currently
managing. This allows the tree to be navigated without executing it,
and allows special tasks such as diagramming the tree to be
accomplished.

Controllers represented by classes with a :meth:`__call__` method can
simply define a :attr:`children` instance attribute or
property. Controllers represented by functions can use Python's
ability to have function data, as follows::

    def view1(request):
        return view2(request)
    view1.children = [view2]

Some controllers may select different children depending on the
context, in this case the :attr:`children` attribute should hold all
of the possible children.

In rarer cases there may be an infinite or undecidable set of
children. In this case the :attr:`children` mechanism breaks down, and
should be omitted.

Any controller without a :attr:`children` attribute is considered to
be equivalent to having an attribute containing the empty list. So
there's no need to add the attribute to the tree's leaves.



.. rubric:: Footnotes

.. [#f1] This is sometimes colloquially called `Turtles all the Way
   Down
   <http://en.wikipedia.org/wiki/Turles_all_the_way_down>`_. Simon
   Willison was the first I came across using this phrase to talk
   about recursive web-frameworks.