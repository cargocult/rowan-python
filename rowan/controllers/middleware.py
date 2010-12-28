from time import time
import urlparse
import uuid

import base
from rowan.utils.subdicts import ChangeTrackingDict
import rowan.http as http

class SessionMiddleware(base.Wrapper):
    """
    Wraps another controller, doing the session lookup before
    delegating. The database middleware must be called before this.
    """
    def __call__(self, request):
        assert request.db, "Create a database before using sessions."

        # Assume we need a new session unless we find otherwise.
        create_cookie = False
        make_new_session = True

        # See if we have a current session id.
        session_id = request.cookies.get('session')
        if session_id:

            # Look up the session
            session_data = request.db.session.find_one({"id": session_id})
            if session_data:
                assert session_data['type'] == "session"

                # Time-out sessions, and check for IP-hacking.
                if session_data['expires'] < time():
                    # TODO: Log this failure to help with IP blacklisting.
                    session_data = None

                elif session_data['ip'] != request.REQUEST["REMOTE_ADDR"]:
                    # TODO: Log this failure to help with IP blacklisting.
                    session_data = None

                else:
                    # We have a valid session ready to use.
                    make_new_session = False

            else:
                # TODO: We've got an unknown session key, log this request to
                # help with IP blacklisting.
                pass

        if make_new_session:
            # Create a session, we know we have no user.
            session_id = str(uuid.uuid4())
            request.session_info = session_id
            create_cookie = True

            # Configure the session object for the database
            session_data = {
                "id": session_id,
                "type": "session",
                "ip": request.REQUEST.get("REMOTE_ADDR"),
                "expires": time() + 3600
                }

        # Delegate to generate the result, then add session tracking.
        with request.set(session=session_data):
            result = self.controller(request)

        # Add a cookie if we need to track a new or changed session.
        if create_cookie: result.set_cookie('session', session_id)

        # Finally save the session (this needs to be done always, to
        # keep the expiry up to date).
        session_data['expires'] = time() + 3600
        request.db.session.save(session_data)

        return result

class UserMiddleware(base.Wrapper):
    """
    Wraps another controller, doing the user object lookup - the
    session MUST be set-up before this is called.
    """
    def __call__(self, request):
        assert request.session, "Create a session before dealing with users."

        # Assume we don't have a user.
        request.user = None

        # Try to find a user.
        user_id = request.session.get('user_id', None)
        user_obj = None
        if user_id:
            # Get the user object associated with this session.
            user_obj = request.db.user.find_one({"id":user_id})
            if not user_obj:
                # We had a user-id but it is not valid, so remove it.
                del request.session['user_id']
            else:
                user_obj = ChangeTrackingDict(user_obj)

        # Delegate to generate the result.
        with request.set(user=user_obj):
            result = self.controller(request)

        # Save if modified
        if user_obj and user_obj.dirty:
            request.db.user.save(user_obj)
            user_obj.clean()

        return result

class APIKeyMiddleware(base.Wrapper):
    """
    Wraps another controller, making sure any incoming requests have a
    valid API key for the associated location.
    """
    def __call__(self, request):
        assert request.db, "Create a database before checking for the API key."

        # Early out if we already have an api
        if hasattr(request, 'api'):
            return self.controller(request)

        # API keys are given either in the query params or POST data.
        api_key = request.body_params.get('api_key')
        if api_key:
            api_key = api_key[0].strip().lower()

            # We must have a location, to check if the request came
            # from the correct place.
            from_location = request.body_params.get('from')
            if from_location:
                from_location_domain = urlparse.urlparse(from_location).netloc

                # Find the api key in the database matching the given
                # domain. So we can fail by either not having the key, or
                # not having the domain.
                api_data = request.db.api.find_one(
                    {"id": api_key, "domains": from_location_domain}
                    )
                if api_data:
                    assert api_data['type'] == "api"
                    request.api = ChangeTrackingDict(api_data)

                    # We've validated the API, so call our wrapped
                    # controller.
                    result = self.controller(request)

                    # Save the api data if we need to.
                    if request.api.dirty:
                        request.db.api.save(request['api'])
                        request.apit.save()

                    return result
                else:
                    self.get_logger().info("Unknown key %s" % api_key)
            else:
                self.get_logger().info("No from_location")
        else:
            self.get_logger().info("No API key given")

        raise http.HttpError("API Key Error", 403)
