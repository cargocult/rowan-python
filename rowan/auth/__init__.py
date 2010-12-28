# For the benefit of those who import us
from twitter import *
from facebook import *

# Functionality for this module
import rowan.http as http

def DEBUG_insecure_login(request):
    """
    A controller that logs the user into into the current session,
    based solely on the user-id they specify in the incoming
    data. This is obviously totally insecure, and is for debugging
    only.
    """
    user_id = request.query_params.get("user_id", [])
    if len(user_id) != 1:
        raise http.HttpError("Expected a user_id in query data.", 400)

    user_id = user_id[0]
    user_cnt = request.db.user.find({"id": user_id}).count()
    if user_cnt == 1:
        # Update the session
        request.session['user_id'] = user_id

    # Send them home.
    return http.Http302("/")

