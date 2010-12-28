import rowan.controllers.base as base

# ----------------------------------------------------------------------------

import pymongo

class DBMiddleware(base.Wrapper):
    """
    Wraps another controller, setting up the mongo database before
    delegation. The database is housed in the .db property of the
    request.
    """
    def __init__(self, controller,
                 server="localhost", port=27017, db="test"):
        super(DBMiddleware, self).__init__(controller)
        self.server = server
        self.port = port
        self.db = db

    def __call__(self, request):
        connection = pymongo.Connection(self.server, self.port)
        with request.set(db=connection[self.db]):
            return self.controller(request)

# ----------------------------------------------------------------------------

import sqlalchemy as sql
import sqlalchemy.orm as orm

def get_sql_engine(connection_string):
    """Creates an sql database engine. This is a separate function so
    it can also be called from separate modules without loading the
    middleware.
    """
    return sql.create_engine(connection_string, echo=True)

class SQLMiddleware(base.Wrapper):
    """Wraps another controller, setting up the sql database before
    delegation. The database is housed in the .sql property of the
    request.
    """
    def __init__(self, controller, connection_string="sqlite:///database.db"):
        super(SQLMiddleware, self).__init__(controller)
        self.connection_string = connection_string

    def __call__(self, request):
        engine = get_sql_engine(self.connection_string)
        with request.set(sql=orm.sessionmaker(bind=engine)()):
            return self.controller(request)

