from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean
from sqlalchemy import ForeignKey, UniqueConstraint, create_engine
from sqlalchemy.orm import relationship, backref, sessionmaker
from flask.ext.login import (UserMixin,AnonymousUser)

class Base(object):
    id = Column(Integer, primary_key=True)
Base = declarative_base(cls=Base)

class FeedUser(Base,UserMixin):
    __tablename__ = 'feed_user'

    email = Column(String, unique=True)
    name = Column(String)
    password = Column(String)
    oauth_id = Column(String)
    active = Column('active', Boolean(), default=True)

    def __init__(self, oauth_id, name, password, email):
        self.oauth_id = oauth_id
        self.name = name
        self.password = password
        self.email = email
        
    def __repr__(self):
        return '<FeedUser({0})>'.format(self.email)

    def is_active(self):
        return self.active;

    def get_id(self):
        return self.oauth_id

    @staticmethod
    def load(oauth_id):
        try:
            user = session.query(FeedUser).filter_by(oauth_id=oauth_id).one()
            return user
        except:
            return None

    @staticmethod
    def add(**data):
        if 'user_id' in data:
            usr_id = data['user_id']
        else:
            usr_id = data['id']
        if 'name' in data:
            nme = data['name']
        else:
            nme = ''
        if 'password' in data:
            password = data['password']
        else:
            password = ''
        if 'email' in data:
            email = data['email']
        else:
            email = ''
        user = FeedUser(usr_id,nme,password,email)
        session.add(user)
        session.commit()
        return user

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

class Anonymous(AnonymousUser):
    __tablename__ = "Anonymous"

engine = create_engine('sqlite:///hqfeed.db', echo=True)

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

t = FeedUser(email='arjun@hqfeed.com',name='Arjun Suresh', password="something",oauth_id='asd')
#f = Feeds(FeedUser=f,name='Mathematics')

#conn = engine.connect()
#conn.execute(t)
