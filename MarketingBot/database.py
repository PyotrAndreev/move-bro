from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, create_engine, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

DATABASE_URL = "postgresql://postgres:001452@localhost:5432/mydatabase"

engine = create_engine(DATABASE_URL)

Base = declarative_base()

class Users(Base):
    tablename = 'Users'
    user_id = Column(Integer, primary_key=True, unique=True, nullable=False)
    name = Column(String)
    username = Column(String, nullable=False)
    bot_id = Column(Integer, ForeignKey('Bots.bot_id'))
    phone = Column(Integer)
    description = Column(String)
    last_online = Column(String, default="recently")
    banned = Column(Boolean, nullable=False, default=False)
    messages = relationship('Messages', back_populates='user')
    bot = relationship('Bots', back_populates='users')


class Bots(Base):
    tablename = 'Bots'
    bot_id = Column(Integer, primary_key=True, unique=True, nullable=False)
    active = Column(Boolean, nullable=False)
    login_data = Column(String)
    users = relationship('Users', back_populates='bot')
    messages = relationship('Messages', back_populates='bot')
    logs = relationship('Logs', back_populates='bot')


class Messages(Base):
    tablename = 'Messages'
    message_id = Column(Integer, primary_key=True, unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey('Users.user_id'))
    bot_id = Column(Integer, ForeignKey('Bots.bot_id'))
    content = Column(String, nullable=False)
    date = Column(TIMESTAMP, nullable=False)
    user = relationship('Users', back_populates='messages')
    bot = relationship('Bots', back_populates='messages')


class Logs(Base):
    tablename = 'Logs'
    log_id = Column(Integer, primary_key=True, unique=True, nullable=False)
    action = Column(String, nullable=False)
    date = Column(TIMESTAMP, nullable=False)
    bot_id = Column(Integer, ForeignKey('Bots.bot_id'))
    bot = relationship('Bots', back_populates='logs')


Base.metadata.create_all(engine)