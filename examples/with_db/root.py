from __future__ import with_statement
import os
import logging

import jinja2
import sqlalchemy

from rowan import http
from rowan.controllers import *

import urls
import models

# Our root controller.
def _create_root_node():
    # Set up the services.
    template_path = os.path.join(os.path.dirname(__file__), 'templates')
    templates = jinja2.Environment(
        loader=jinja2.FileSystemLoader(template_path)
        )

    session_class = models.create_session_class()

    # Create the top level tree nodes.
    master_urls = urls.master_urls
    error_handler = ErrorHandler(master_urls)
    return SetParams(
        error_handler,
        services__templates=templates,
        services__db=session_class
        )

root = _create_root_node()
