from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship, backref

class Base(object):
    id = Column(Integer, primary_key=True)
Base = declarative_base(cls=Base)

class FeedUser(Base):
    __tablename__ = 'feed_user'

    email = Column(String, unique=True)
    name = Column(String, nullable=False)
    password = Column(String)

    def __repr__(self):
        return '<FeedUser({0})>'.format(self.email)

class Feeds(Base):
    __tablename__ = 'feeds'

    feed_user_id = Column(Integer, ForeignKey('feed_user.id', ondelete="CASCADE"), nullable=False, index=True)
    FeedUser = relationship("FeedUser", backref=backref('feedusers', order_by='Feeds.id'))
    mongo_feed_id = Column(String, nullable = False)
    feed_label = Column(String)
    is_read = Column(Boolean, nullable =True)
    is_starred = Column(Boolean, nullable = True)

    def __repr__(self):
        return '<Feeds({0})>'.format(self.mongo_feed_id)


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///hqfeed.db', echo=True)

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

t = FeedUser(email='chandu@hqfeed.com',name='Chandrashekar Jayaraman', password="something")
#f = Feeds(FeedUser=f,name='Mathematics')

#conn = engine.connect()
#conn.execute(t)
