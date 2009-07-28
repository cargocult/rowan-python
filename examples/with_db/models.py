import os.path
from datetime import datetime

import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base

def create_engine():
    """Create the default engine for this set of models."""
    return sqlalchemy.create_engine(
        'sqlite:///%s/database.db' % os.path.join(os.path.dirname(__file__)), 
        echo=True
        )

def create_session_class():
    """Create a class that we can use to instantiate new sessions."""
    return sqlalchemy.orm.sessionmaker(bind=create_engine())
    
    
# This application's models:
Base = declarative_base()

class BlogEntry(Base):
    """One entry in our blog."""
    
    __tablename__ = 'blogentries'
    
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    title = sqlalchemy.Column(sqlalchemy.Unicode(64))
    date = sqlalchemy.Column(sqlalchemy.DateTime())
    content = sqlalchemy.Column(sqlalchemy.UnicodeText())
    
    def __init__(self, title, date=None, content=""):
        self.title = title
        self.date = date if date is not None else datetime.now()
        self.content = content
        
    def __unicode__(self):
        return self.title
        
        
if __name__ == '__main__':
    engine = create_engine()
    Base.metadata.create_all(engine)
    
    # Create a couple of random entries
    session = create_session_class()()
    
    entries = session.query(BlogEntry).all()
    for i in range(len(entries), 2):
        entry = BlogEntry('Blog Entry Number %d' % (i+1))
        entries.append(entry)
        session.add(entry)
        
    if session.dirty: session.commit()
        
