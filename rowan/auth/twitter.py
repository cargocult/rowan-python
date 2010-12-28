"""Authentication against the twitter OAUTH api."""

import urlparse

import oauth2 as oauth

import base
import rowan.controllers as controllers
import rowan.http as http

TWITTER_OAUTH = {
    # These are application specific and need to be set accordingly.
    "consumer_key": "Db5cXiAIHjmzqNwmlddaMg",
    "consumer_secret": "gwzJ7AAUXMXsvwAz3T5VELoJSpnZSWcfiP1DAMjdDA",

    # These should be fine, unless twitter changes its API
    "host": "api.twitter.com",
    "callback": "http://localhost:8000/auth/twitter/done/",

    "request_token": {
        "resource": "/oauth/request_token",
        "method": "POST",
        },
    "user_authorization": {
        "resource": "/oauth/authorize",
        "method": "GET"
        },
    "access_token": {
        "resource": "/oauth/access_token",
        "method": "POST"
        }
    }
class TwitterOAuthError(Exception): pass

class TwitterAuthChannel(base.AuthChannel):
    """Encapsulates the handling of twitters authentication data and
    its storage in our database structure."""

    def get_channel_key(self):
        return "twitter"

    def create_session_data(self):
        return {
            'token': self.data['oauth_token'],
            'secret': self.data['oauth_token_secret'],
            }

    def create_user_data(self):
        return {
            'user_id': self.data['user_id'],
            'user_name': self.data['screen_name']
            }

    def create_auth_data(self):
        return {
            "twitter_id": self.data['user_id']
            }

    def get_auth_data(self, db):
        auth_table_name = self.get_auth_table_name()
        return db[auth_table_name].find_one(
            {'twitter_id': self.data['user_id']}
            )

consumer = oauth.Consumer(
    TWITTER_OAUTH['consumer_key'],
    TWITTER_OAUTH['consumer_secret']
    )

def twitter_begin_auth(request):
    """Initiate the authentication against the twitter oauth
    server."""
    client = oauth.Client(consumer)

    action = TWITTER_OAUTH['request_token']
    host = TWITTER_OAUTH['host']
    url = "http://%s%s" % (host, action['resource'])
    resp, content = client.request(
        url, action['method'],
        "oauth_callback=%s" % TWITTER_OAUTH['callback']
        )
    if resp['status'] != "200":
        raise TwitterOAuthError("Invalid response '%s'." % resp['status'])
    else:
        # Write the auth token to the session
        twitter_data = dict(urlparse.parse_qsl(content))
        request.session['twitter'] = {
            "token": twitter_data['oauth_token'],
            "secret": twitter_data['oauth_token_secret']
            }

    # Redirect the user to the twitter login screen
    action = TWITTER_OAUTH['user_authorization']
    url = "http://%s%s?oauth_token=%s" % (
        host, action['resource'], twitter_data['oauth_token']
        )
    return http.Http302(location=url)

def twitter_end_auth(request):
    """This is called by Twitter when the user has granted permission
    to the app."""
    # Create a temporary client based on the temporary token data.
    token = oauth.Token(
        request.session['twitter']['token'],
        request.session['twitter']['secret']
        )
    token.set_verifier(request.query_params['oauth_verifier'])
    client = oauth.Client(consumer, token)

    # Get the permanent token data from the above verifier.
    action = TWITTER_OAUTH['access_token']
    host = TWITTER_OAUTH['host']
    url = "http://%s%s" % (host, action['resource'])
    resp, content = client.request(url, action['method'])
    if resp['status'] != "200":
        raise TwitterOAuthError("Invalid response '%s'." % resp['status'])
    else:
        # Finish the authentication process.
        twitter_data = dict(urlparse.parse_qsl(content))
        auth = TwitterAuthChannel(twitter_data)
        auth.complete_authentication(request.db, request.session)

    # Redirect somewhere useful
    return http.Http302(location="/")

# Holds all the twitter related authentication urls.
twitter_router = controllers.Router(
    (r"^$", twitter_begin_auth),
    (r"^done/$", twitter_end_auth)
    )
