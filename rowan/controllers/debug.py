"""A filter for turning json into viewable HTML."""

import json
import cgi

import rowan.http as http
import base

class JSONViewer(base.Wrapper):
    """
    This wrapper is designed to wrap any controller that is likely to
    generate JSON results. If the controller returns JSON in a 200
    HTTP response code, then it will render the result into HTML and
    return a HTML response. Any other response passes through
    untouched.
    """

    def __call__(self, request):
        response = self.controller(request)
        if (response.status_code != 200 or
            response.content_type != "application/json"):
            return response

        # Parse the json
        json_data = json.loads(response.content)

        # Create the HTML response
        response = http.HttpResponse(content_type = "text/html")
        response.write(before)
        self._output(response, json_data)
        response.write(after)
        return response

    def _output(self, response, data):
        if isinstance(data, list):
            self._output_array(response, data)
        elif isinstance(data, dict):
            self._output_object(response, data)
        elif data in (True, False):
            self._output_boolean(response, data)
        elif isinstance(data, basestring):
            self._output_string(response, data)
        else:
            self._output_number(response, data)

    def _output_boolean(self, response, boolean):
        response.write("<div class='boolean'>%s</div>" % str(boolean).lower())

    def _output_string(self, response, literal):
        response.write(
            "<div class='string'>\"%s\"</div>" % cgi.escape(literal)
            )

    def _output_number(self, response, literal):
        response.write("<div class='number'>%s</div>" % str(literal))

    def _output_object(self, response, obj):
        response.write("<div class='object'>")
        count = len(obj)
        if count:
            response.write("<table>")
            for key, value in sorted(obj.items()):
                response.write("<tr><th>%s:</th><td>" % cgi.escape(key))
                self._output(response, value)
                response.write("</td></tr>")
            response.write("</table>")
        else:
            response.write("{}")

        response.write("</div>")

    def _output_array(self, response, seq):
        response.write("<div class='array'>")
        count = len(seq)
        if count:
            response.write("<table>")
            for i, item in enumerate(seq):
                response.write("<tr><th>%d</th><td>" % i)
                self._output(response, item)
                response.write("</td></tr>")
            response.write("</table>")
        else:
            response.write("[]")
        response.write("</div>")

class OptionalJSONViewer(JSONViewer):
    """
    This wrapper is a JSONViewer only when 'format=html' is passed into the
    request.
    """
    def __call__(self, request):
        if request.query_params.get('format', None) == ['html']:
            return JSONViewer.__call__(self, request)
        else:
            return self.controller(request)

before = """
<!DOCTYPE HTML><html><head><style>
body { line-height: 16px; font-size: 14px; font-family: sans; }
table { border: 1px solid black; background-color: white; }
table tr { vertical-align: top; }
.array table tr:nth-child(odd) { background-color: #dee; }
.array table tr:nth-child(even) { background-color: #eff; }
.object table tr:nth-child(odd) { background-color: #ede; }
.object table tr:nth-child(even) { background-color: #fef; }
.boolean { color: #600; }
.string { color: #060; }
.number { color: #009; }
th { text-align: left; padding: 2px 10px 2px 2px; font-weight: normal; }
td { padding: 2px; }
p { margin: 0; padding: 0; font-style: italic; color: #999 }
.array th { font-style: italic; color: #999 }
</style></head><body><h1>JSON Result - Debug View</h1>
"""
after = """</body></html>"""


