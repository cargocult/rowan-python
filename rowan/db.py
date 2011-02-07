import rowan.controllers.base as base

# ----------------------------------------------------------------------------

class MongoDBMiddleware(base.Wrapper):
    """
    Wraps another controller, setting up the mongo database before
    delegation. The database is housed in the .db.mongo property of the
    request.
    """
    @classmethod
    def import_dependencies(cls):
        global pymongo
        import pymongo

    def __init__(self, controller,
                 server="localhost", port=27017, db="test"):
        super(DBMiddleware, self).__init__(controller)
        self.server = server
        self.port = port
        self.db = db
        self.connection = pymongo.Connection(self.server, self.port)

    def __call__(self, request):
        with request.set(db__mongo=self.connection[self.db]):
            return self.controller(request)

# ----------------------------------------------------------------------------

class SQLAlchemyMiddleware(base.Wrapper):
    """Wraps another controller, setting up the sql database before
    delegation. The database is housed in the .db.sqlalechmy property of
    the request.
    """
    @classmethod
    def import_dependencies(cls):
        global sql, orm
        import sqlalchemy as sql
        import sqlalchemy.orm as orm

    def __init__(self, controller, connection_string="sqlite:///database.db"):
        super(SQLAlchemyMiddleware, self).__init__(controller)
        self.connection_string = connection_string

    def __call__(self, request):
        engine = sql.create_engine(self.connection_string, echo=True)
        with request.set(db__sqlalchemy=orm.sessionmaker(bind=engine)()):
            return self.controller(request)

