from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean, Table
from sqlalchemy import ForeignKey, UniqueConstraint, create_engine
from sqlalchemy.orm import relationship, backref, sessionmaker
from flask.ext.login import (UserMixin,AnonymousUser)

class Base(object):
    id = Column(Integer, primary_key=True)
Base = declarative_base(cls=Base)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///hqfeed.db', echo=True)

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

feeds_tags = Table('feeds_tags', Base.metadata,
                   Column('feeds_id', Integer, ForeignKey('feeds.id')),
                   Column('tag_id', Integer, ForeignKey('tags.id')))

def _unique(session, cls, hashfunc, queryfunc, constructor, arg, kw):
    cache = getattr(session, '_unique_cache', None)
    if cache is None:
        session._unique_cache = cache = {}

    key = (cls, hashfunc(*arg, **kw))
    if key in cache:
        return cache[key]
    else:
        with session.no_autoflush:
            q = session.query(cls)
            q = queryfunc(q, *arg, **kw)
            obj = q.first()
            if not obj:
                obj = constructor(*arg, **kw)
                session.add(obj)
        cache[key] = obj
        return obj

def unique_constructor(scoped_session, hashfunc, queryfunc):
    def decorate(cls):
        def _null_init(self, *arg, **kw):
            pass
        def __new__(cls, bases, *arg, **kw):
            # no-op __new__(), called
            # by the loading procedure
            if not arg and not kw:
                return object.__new__(cls)

            # session = scoped_session()

            def constructor(*arg, **kw):
                obj = object.__new__(cls)
                obj._init(*arg, **kw)
                return obj

            return _unique(
                        scoped_session,
                        cls,
                        hashfunc,
                        queryfunc,
                        constructor,
                        arg, kw
                   )

        # note: cls must be already mapped for this part to work
        cls._init = cls.__init__
        cls.__init__ = _null_init
        cls.__new__ = classmethod(__new__)
        return cls

    return decorate
    
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

    # many to many Feeds<->Tag
    tags = relationship('Tag', secondary=feeds_tags, backref='tags')
    def __repr__(self):
        return '<Feeds({0})>'.format(self.mongo_feed_id)

@unique_constructor(session,
        lambda tag: tag,
        lambda query, tag: query.filter(Tag.tag == tag)
)        
class Tag(Base):
    __tablename__ = 'tags'

    tag = Column(String(50), nullable=False, unique=True)

    def __init__(self, tag):
        self.tag = tag
        
    def __repr__(self):
        return '<Tags({0})>'.format(self.tag)
        
class Anonymous(AnonymousUser):
    __tablename__ = "Anonymous"

class FeedsUpdate(Base):
    __tablename__ = 'feeds_update'

    feed_url = Column(String, nullable=False)
    last_updated_title = Column(String)
    last_updated_date = Column(String)

    def __repr__(self):
        return '<FeedsUpdate({0})>'.format(self.feed_url)
    

#t = FeedUser(email='chandu@hqfeed.com',name='Chandrashekar Jayaraman', password="something")
#t = session.query(FeedUser)[0]
#f = Feeds(FeedUser=f,name='Mathematics')

#conn = engine.connect()
#conn.execute(t)
