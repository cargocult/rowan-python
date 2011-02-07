"""Authentication against the Facebook ouath2 api."""

import urllib, urlparse, json

import base
import rowan.controllers as controllers
import rowan.http as http

FACEBOOK_OAUTH = {
    # These should be fine, unless Facebook changes its API
    "host": "graph.facebook.com",

    "user_authorization": "/oauth/authorize",
    "access_token": "/oauth/access_token",
    "profile": "/me",
    }
class FacebookOAuthError(Exception): pass

class FacebookAuthChannel(base.AuthChannel):
    """
    Encapsulates the handling of Facebook's authentication data and
    its storage in a database.
    """
    def get_channel_key(self):
        return "facebook"

    def create_session_data(self):
        return {
            'access_token': self.data['access_token'],
            'permissions': self.data['permissions']
            }

    def create_user_data(self):
        return {
            'user_id': self.data['uid'],
            'user_name': self.data['name']
            }

    def create_auth_data(self):
        return {
            "facebook_id": self.data['uid']
            }

    def get_auth_data(self, db):
        auth_table_name = self.get_auth_table_name()
        return db[auth_table_name].find_one(
            {'facebook_id': self.data['uid']}
            )

def facebook_begin_auth(request):
    """
    Initiate the authentication against the Facebook oauth2 server.
    """
    # Redirect the user to the Facebook login screen
    host = FACEBOOK_OAUTH['host']
    action = FACEBOOK_OAUTH['user_authorization']
    params = dict(
        client_id=request.auth.facebook['client_id'],
        redirect_uri=request.auth.facebook['redirect_uri'],
        scope=request.auth.facebook['permissions']
        )
    url = "https://%s%s?%s" % (
        host, action, urllib.urlencode(params)
        )
    return http.Http302(location=url)

def facebook_end_auth(request):
    """
    This is called by Facebook when the user has granted permission to
    the app.
    """
    host = FACEBOOK_OAUTH['host']
    action = FACEBOOK_OAUTH['access_token']
    params = dict(
        client_id=request.auth.facebook['client_id'],
        redirect_uri=request.auth.facebook['redirect_uri'],
        client_secret=request.auth.facebook['client_secret'],
        code=request.query_params['code'][0]
        )
    response = urllib.urlopen(
        "https://%s%s?%s" % (host, action, urllib.urlencode(params))
        ).read()
    response = urlparse.parse_qs(response)
    access_token = response['access_token'][-1]

    action = FACEBOOK_OAUTH['profile']

    profile = json.load(urllib.urlopen(
                "https://%s%s?%s" % (host, action,
                urllib.urlencode(dict(access_token=access_token)))))

    data = dict(
        access_token=access_token,
        permissions=request.auth.facebook['permissions'],
        uid=profile['id'],
        name=profile['name']
        )

    auth = FacebookAuthChannel(data)
    auth.complete_authentication(request.db, request.session)

    # Redirect somewhere useful
    return http.Http302(location=request.auth.facebook['complete_uri'])

# Holds all the Facebook related authentication urls.
facebook_router = controllers.Router(
    (r"^$", facebook_begin_auth),
    (r"^done/$", facebook_end_auth)
    )
