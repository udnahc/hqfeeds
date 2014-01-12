from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean, Table
from sqlalchemy import ForeignKey, UniqueConstraint, create_engine, ForeignKeyConstraint
from sqlalchemy.orm import relationship, backref, sessionmaker
from flask.ext.login import UserMixin
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session


engine = create_engine('sqlite:////sarjun/instances/hqfeeds/hqfeeds.db', echo=True)
Session = sessionmaker(bind=engine)
dbsession = scoped_session(sessionmaker(autocommit=False,
                                        autoflush=False,
                                         bind=engine))
class Base(object):
    id = Column(Integer, primary_key=True)
    
Base = declarative_base(cls=Base)
Base.query = dbsession.query_property()

feeds_tags = Table('feeds_tags', Base.metadata,
                   Column('feeds_id', Integer, ForeignKey('feeds.id')),
                   Column('tag_id', Integer, ForeignKey('tags.id')),

                   # Column('feeds_id', Integer),
                   # Column('tag_id', Integer),
                   # ForeignKeyConstraint(
                   #     ["feeds_id", "tag_id"],
                   #     ["feeds.id", "tags.id"],
                   #     name="fk_favorite_entry", use_alter=True
                   # )
)

class FeedUser(Base,UserMixin):
    __tablename__ = 'feed_user'

    email = Column(String, unique=True)
    name = Column(String)
    password = Column(String)
    oauth_id = Column(String)
    active = Column('active', Boolean(), default=True)

#    feeds = relationship("Feeds", backref="feeduser")

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
            user = dbsession.query(FeedUser).filter_by(oauth_id=oauth_id).one()
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
            name = data['name']
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
        dbsession.add(user)
        dbsession.commit()
        return user

class User(Base):
    __tablename__ = 'users'
    id = Column('user_id', Integer, primary_key=True)
    name = Column(String)    
    email = Column(String, unique=True)
    oauth_token = Column(String(200))
    oauth_secret = Column(String(200))
    oauth_id = Column(String)
    active = Column('active', Boolean(), default=True)

class Feeds(Base):
    __tablename__ = 'feeds'

    mongo_feed_id = Column(String, nullable = False)
    feed_title = Column(String)    

    # many to many Feeds<->Tag
    tags = relationship('Tag', secondary=feeds_tags, backref='feeds')
    def __repr__(self):
        return '<Feeds({0})>'.format(self.mongo_feed_id)

class Tag(Base):
    __tablename__ = 'tags'
    tag = Column(String(50), nullable=False)

    def __init__(self,tag):
        self.tag = tag
        
    def __repr__(self):
        return '<Tags({0})>'.format(self.tag)
        
class FeedsUpdate(Base):
    __tablename__ = 'feeds_update'

    feed_url = Column(String, nullable=False)
    last_updated_title = Column(String)
    last_updated_date = Column(String)

    def __repr__(self):
        return '<FeedsUpdate({0})>'.format(self.feed_url)
    
# t = FeedUser(oauth_id="something", email='chandu@hqfeed.com',name='Chandrashekar Jayaraman', password="something")
# dbsession.add(t)
# dbsession.commit()
#t = dbsession.query(FeedUser)[0]
#print t
#f = Feeds(FeedUser=t,name='Mathematics')
#Base.metadata.create_all(engine)

# conn = engine.connect()
# conn.execute(t)
