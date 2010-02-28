Model, View, Controller and Context
===================================

Rowan is an MVC based web-framework. That means it splits its code
into three concerns: the model, the view and the controller.

MVC
***

The Model
---------

The model holds the data for a web-application. It consists of the
code to talk to the database, to store and validate data and the
retrieve it when it is needed. You'll typically need to write model
code, but you won't use the Rowan library directly to do so. Rowan
provides no model-layer.

I'd suggest you use either Python's basic database API, or a fully
featured Object Relational Mapping system such as SQL Alchemy.

The View
--------

The view controls what pages on the site should look and feel
like. This includes both the visuals, and the user experience
concerns.

Again, like the model layer, you'll have to write lots of view code
for any reasonable web application. And again, you'll not use Rowan to
do that.

There are lots of options for libraries that can generate nice HTML /
XML code according to templates you specify. I use Jinja2, which is based
on Django's templating language.


The Controller
--------------

This third element *is* what you'll use Rowan to write. Controllers
are the central point of responsibility for marshalling content in the
model layer into representations in the view layer. 

They are used in two contexts: some controllers can be asked to
display appropriate information. They query that information from the
model layer, choose a suitable format from the view layer, and output
the merged data. Other controllers receieve data from the user (as a
result of a form-submission, for example, or from an API call), and
write that data out to the model layer, then send some confirmation or
other data out through the view layer.

Controllers control the web-application. They respond to a request
(with or without data) and generate a response. This request-response
paradigm is what makes Rowan's controllers very powerful, and allows
them to be composed into the trees that give the framework its name.


Nomenclature
------------

MVC is a common paradigm of software development, but unfortunately it is very
ambiguous. It seems to me that everyone I've heard talk about MVC has a
different idea of exactly why, where and how the dividing lines between each
unit should be drawn.

In Django, for example, controllers are confusingly called 'views', and what we
call views are 'templates' (although some of Django's view code I'd also
consider to be at the view layer in a MVC structure). I'm following roughly the
nomenclature of Ruby on Rails. Microsoft advocated MVC development for the .NET
platform, but its Views include a lot of what I call a controller here. And so
on...

That's not to say that for any particular choice of MVC that things are
confusing. In Rowan, it is pretty clear where the dividing lines between
elements are, because the framework delegates both Model code and View code to
other libraries and makes no requirements how you achieve either.

Context
*******

The context isn't code you have to write, it is the name for the
settings and properties that are in effect when a controller is asked
to generate a response.

Some of the context depends on the request itself: the user's
identity, for example, or the URL they asked for. Other bits of
context control how the rest of the code should do its job: where on
the hard-drive the HTML template files are kept, for example, or the
name of the database to connect to. This latter type of context information 
you might expect to be either found in a configuration or settings file (as 
in Django), or be dictated by convention and hard-coded into the framework
(as in Rails).

One of the most powerful and unusual features of Rowan is its
ability to have context change when a request is being processed. In
Rowan, controllers work together to generate a response for the
user. One controller can temporarily change or add to the context for
its collaborators.

This makes it easier to build applications that are reusable, because
they don't typically have to worry about having the correct settings
configured globally - they can just adjust the context in the way they
need and those adjustments will be temporary and not affect any other
part of the code.

The next section, on the Rowan Tree, has more details on how this
happens.