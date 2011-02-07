from __future__ import with_statement
import os
import logging

import jinja2
import sqlalchemy

from rowan import http
from rowan.controllers import *
from rowan import db

import urls
import models

# Our root controller.
def _create_root_node():
    # Set up the services.
    template_path = os.path.join(os.path.dirname(__file__), 'templates')
    templates = jinja2.Environment(
        loader=jinja2.FileSystemLoader(template_path)
        )

    connection_string = 'sqlite:///%s/database.db' % \
        os.path.abspath(os.path.join(os.path.dirname(__file__)))

    # Create the top level tree nodes.
    root = SetParams(
        ErrorHandler(
            db.SQLAlchemyMiddleware(
                urls.master_urls,
                connection_string=connection_string
                )
            ),
        services__templates=templates
        )
    return root

root = _create_root_node()
