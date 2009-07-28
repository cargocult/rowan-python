import os.path
from datetime import datetime

import sqlalchemy as db
import sqlalchemy.orm as orm
from sqlalchemy.ext.declarative import declarative_base

def create_engine():
    """Create the default engine for this set of models."""
    return db.create_engine(
        'sqlite:///%s/database.db' % os.path.join(os.path.dirname(__file__)), 
        echo=True
        )

def create_session_class():
    """Create a class that we can use to instantiate new sessions."""
    return db.orm.sessionmaker(bind=create_engine())
    
    
# This application's models:
Base = declarative_base()

entry_categories = db.Table('entry_categories', Base.metadata,
    db.Column('blog_entry_id', db.Integer, db.ForeignKey('blogentries.id')),
    db.Column('cateogry_id', db.Integer, db.ForeignKey('categories.id')),
    )

class Category(Base):
    """A category into which a blog post may fit."""
    
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Unicode(64))
    
    def __init__(self, title):
        self.title = title
        
    def __unicode__(self):
        return self.title

class BlogEntry(Base):
    """One entry in our blog."""
    
    __tablename__ = 'blogentries'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Unicode(64))
    date = db.Column(db.DateTime())
    content = db.Column(db.UnicodeText())
    
    categories = orm.relation(
        Category, secondary=entry_categories, backref='entries'
        )
    
    def __init__(self, title, date=None, content=""):
        self.title = title
        self.date = date if date is not None else datetime.now()
        self.content = content
        
    def __unicode__(self):
        return self.title

class Comment(Base):
    """A comment on one blog entry."""
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)    
    date = db.Column(db.DateTime())
    content = db.Column(db.UnicodeText())
    
    # Define the relationship between database tables and between classes.
    blog_entry_id = db.Column(db.Integer, db.ForeignKey('blogentries.id'))
    blog_entry = orm.relation(
        BlogEntry, backref=orm.backref('comments', order_by='Comment.id')
        )
        
    def __init__(self, date=None, content=""):
        self.date = date if date is not None else datetime.now()
        self.content = content
        
        
if __name__ == '__main__':
    import random
    
    # Build the database
    engine = create_engine()
    Base.metadata.create_all(engine)
    
    
    # Create a couple of random bits of data
    session = create_session_class()()
    
    categories = session.query(Category).all()
    if len(categories) == 0:
        categories = [
            Category('One'),
            Category('Two'),
            Category('Three'),
            Category('Four'),
            Category('Five')
            ]
        session.add_all(categories)
        
    entries = session.query(BlogEntry).all()
    for i in range(len(entries), 6):
        entry = BlogEntry(u'Blog Entry Number %d' % (i+1))
        entries.append(entry)
        session.add(entry)
        
        # Up to five comments
        entry.comments = [
            Comment(content=u"Comment %d" % (j+1))
            for j in range(random.randint(1,5))
            ]
            
        # And a couple of categories
        entry.categories = random.sample(categories, random.randint(0,3))
        
    
    # Send the transaction, if we're done anything.
    if session.dirty or session.new: 
        session.commit()
        
