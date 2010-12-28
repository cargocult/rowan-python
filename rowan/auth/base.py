"""The base class definition for authentication channels."""

import logging

class AuthChannel(object):
    """Represents an authorization system."""

    @classmethod
    def getLogger(cls):
        """Returns a logger for this class, or its children."""
        if not hasattr(cls, '_logger'):
            cls._logger = logging.getLogger(cls.__name__)
        return cls._logger

    def __init__(self, data_from_server):
        """Create a new channel object based on the data returned
        after successfully logging in through this channel."""
        self.data = data_from_server

    def get_auth_table_name(self):
        """Returns the collection used to store this channel's
        authentication data. If you override get_channel_key, this
        method should work without alteration."""
        return "%s_user" % self.get_channel_key()

    def get_channel_key(self):
        """Returns a short human-readable key which is used to store
        this channel's data against both the session and the user.
        This must be defined in subclasses."""
        raise NotImplementedError()

    def create_session_data(self):
        """Returns a JSON-compatible dictionary containing the data
        specific to this channel that needs to be stored in the
        session."""
        return {}

    def create_user_data(self):
        """Returns a JSON-compatible dictionary containing the data
        specific to this channel that needs to be permanently stored
        in the associated user's data."""
        return {}

    def create_auth_data(self):
        """Returns a JSON-compatible dictionary containing the data
        needed to link a user and thier authentication through this
        channel. Typically the channel will generate some id, that
        will be used to lookup the authentication data. The auth data
        set by this method is just a stub (and can often be just the
        channel's id).  To this will be set the associated user id
        ('user_id'), the type ('xxx_user', where xxx is the channel
        key returned from get_channel_key)."""
        return NotImplementedError()

    def get_auth_data(self, db):
        """Returns the authentication data matching this object in the
        given database."""
        return NotImplementedError()

    def complete_authentication(self, db, session):
        """This method is called when the authentication is received,
        to make sure the authentication is correctly associated with a
        user. The method should be completely generic, and should not
        require overriding."""

        # Find this session's user id, if it has one.
        current_user_id = session.get('user_id', None)

        # Try to find the authentication record in the database.
        auth_in_db = self.get_auth_data(db)

        # Other cached data.
        auth_table_name = self.get_auth_table_name()

        # Match the user and their session data.
        user_obj = None
        if current_user_id:
            if auth_in_db:
                if auth_in_db['user_id'] == current_user_id:
                    # This authentication has been used for this user
                    # before, so there's nothing more to do.
                    AuthChannel.getLogger().debug(
                        "Already logged in as authenticated user."
                        )
                else:
                    # We have a mismatch between the user associated
                    # with the authentication, and the user associated
                    # with the current session.
                    AuthChannel.getLogger().debug(
                        "Already logged in as a different user."
                        )

                    if False: # TODO: Check if we can merge
                        # Merge two accounts into one.
                        raise NotImplementedError("Can't merge accounts.")
                    else:
                        # Switch users to the one associated with the new
                        # authentication.
                        current_user_id = auth_in_db['user_id']
                        session['user_id'] = current_user_id
            else:
                # This is the first time we've seen this
                # authentication, so store it as belonging to this
                # user.
                AuthChannel.getLogger().debug(
                    "Adding this authentication to the current user."
                    )
                auth_data = self.create_auth_data()
                auth_data['user_id'] = current_user_id
                auth_data['type'] = auth_table_name
                db[auth_table_name].insert(auth_data)
        else:
            if auth_in_db:
                # This is a regular login - the authentication data is
                # in the database and it is associated with a
                # particular user.
                AuthChannel.getLogger().debug(
                    "Logging in as the authenticated user."
                    )
                current_user_id = auth_in_db['user_id']
                session['user_id'] = current_user_id
                session[self.get_channel_key()] = self.create_session_data()
            else:
                # We don't have a current user, and we've never seen
                # this authentication before. So we create a brand new
                # user for this authentication. NB: Allowing this
                # probably means we have to support merging of
                # accounts, because otherwise a normally
                # Google-authenticating user could sign-in with
                # Twitter, say, creating a new account, then never be
                # able to associate that Twitter account with their
                # main account.
                AuthChannel.getLogger().debug(
                    "Creating a new user for this authentication."
                    )
                raise NotImplementedError("Can't create new users yet.")

        # Update the user data from this authentication.
        if not user_obj:
            user_obj = db.user.find_one({"id":current_user_id})
            assert user_obj

        current_data = user_obj.get(self.get_channel_key)
        new_data = self.create_user_data()
        if current_data != new_data:
            user_auth_data = user_obj.setdefault('auth', {})
            user_auth_data[self.get_channel_key()] = self.create_user_data()
            db.user.save(user_obj)
