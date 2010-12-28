import os
import logging
import jinja2

from rowan import http
from rowan.controllers import *

# View functions
def greet_someone(request):
    logging.getLogger('greet_someone').debug('Called')
    name = request.router_args[0]
    return http.HttpResponse(
        'Hello %s (no %s this time)' % (name, request.settings.shock)
        )

def shock_someone(request):
    logging.getLogger('shock_someone').debug('Called')
    template = request.services.templates.get_template('message.html')
    content = template.render(message=request.settings.shock)
    return http.HttpResponse(content.encode('ascii', 'ignore'))


# Build the root of this application
def _create_root_controller():
    # Create the environment and template loader
    template_path = os.path.join(os.path.split(__file__)[0], 'templates')
    environment = jinja2.Environment(
        loader=jinja2.FileSystemLoader(template_path)
        )

    target_urls = Router(
        (r'^(?P<name>\w+)/$', greet_someone)
        )
    greeting_urls = Router(
        (r'^/hello/', target_urls)
        )
    shock_urls = Router(
        (r'^/boo/', shock_someone)
        )

    site = ErrorHandler(Fallback(
        greeting_urls,
        SetParams(
            shock_urls,
            settings__shock='Boo'
            ),
        status_codes=[404]
        ))

    root = SetParams(site,
        settings__shock='loud shouting',
        services__templates=environment
        )
    return root

root = _create_root_controller()
