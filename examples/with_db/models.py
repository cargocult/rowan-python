import os.path
from datetime import datetime

import sqlalchemy
import sqlalchemy.orm

def create_engine():
    """Create the default engine for this set of models."""
    return sqlalchemy.create_engine(
        'sqlite:///%s/database.db' % os.path.join(os.path.dirname(__file__)), 
        echo=True
        )

def create_session_class():
    return sqlalchemy.orm.sessionmaker(bind=create_engine())
    
metadata = sqlalchemy.MetaData()

# Define the tables
blog_entries = sqlalchemy.Table(
    'blogentries', metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column('title', sqlalchemy.Unicode(64)),
    sqlalchemy.Column('date', sqlalchemy.DateTime()),
    sqlalchemy.Column('content', sqlalchemy.UnicodeText())
)

# Define the ORM-mapped classes
class BlogEntry(object):
    def __init__(self, title, date=None, content=""):
        self.title = title
        self.date = date if date is not None else datetime.now()
        self.content = content
        
    def __unicode__(self):
        return self.title
        
# Bind the classes with the tables.
sqlalchemy.orm.mapper(BlogEntry, blog_entries)

if __name__ == '__main__':
    engine = create_engine()
    metadata.create_all(engine)
    
    # Create a couple of random entries
    session = create_session_class()()
    
    entries = session.query(BlogEntry).all()
    for i in range(len(entries), 2):
        entry = BlogEntry('Blog Entry Number %d' % (i+1))
        entries.append(entry)
        session.add(entry)
        
    if session.dirty: session.commit()
        
