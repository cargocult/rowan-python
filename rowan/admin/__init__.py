import os

import jinja2

import rowan.http as http
import rowan.controllers as controllers

class AdminApp(controllers.Router):
    """
    A Controller that represents an administration application.
    """
    def __init__(self, media_dir="media"):
        path = os.path.abspath(os.path.dirname(__file__))

        # Set up the routing paths.
        assert "/" not in media_dir, "Media dir must be a single directory."
        content_server = controllers.ContentServer(os.path.join(path, "media"))
        super(AdminApp, self).__init__(
            (r"^%s/" % media_dir, content_server),
            (r"^$", self.view_home)
            )

        # Parameter data
        self.media_dir = media_dir

        # Template handling
        template_path = os.path.join(path, 'templates')
        self.template_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(template_path)
            )

    def _render_template(self, template_name, **data):
        template = self.template_env.get_template(template_name)
        if 'media_dir' not in data: data['media_dir'] = self.media_dir
        content = template.render(**data)
        return http.HttpResponse(content.encode('ascii', 'ignore'))

    def view_home(self, request):
        """Displays the summary screen for the homepage of the app."""
        assert request.db
        return self._render_template("home.html")
