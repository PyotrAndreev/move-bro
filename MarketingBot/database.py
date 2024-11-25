import pytz
from datetime import datetime
from sqlalchemy import text, create_engine, Column, Integer, Boolean, String, ForeignKey, DateTime, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session

Base = declarative_base()

class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    tg_id = Column(BigInteger, unique=True)
    name = Column(String, nullable=False)
    lastname = Column(String)
    # bot_username = Column(String, ForeignKey('Bots.username'))
    # bot = relationship('Bots')


class Bots(Base):
    __tablename__ = 'bots'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    tg_id = Column(BigInteger, unique=True)
    admin_id = Column(BigInteger)
    chats = relationship('Chats', back_populates='bot')

class Messages(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True, nullable=False)
    chat_type = Column(String, nullable=False) # dm / pgroup
    chat_name = Column(String, nullable=False) # or id
    message_id = Column(Integer, nullable=False) # inside the chat
    user_username = Column(String, nullable=False)
    bot_username = Column(String, nullable=False)
    content = Column(String, nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)

class Logs(Base):
    __tablename__ = 'logs'
    id = Column(Integer, primary_key=True, nullable=False, unique=True)
    action = Column(String, nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    bot_username = Column(String, ForeignKey('bots.username'), nullable=False)
    bot = relationship('Bots')

class Templates(Base):
    __tablename__ = 'templates'
    id = Column(Integer, primary_key=True)
    content = Column(String, nullable=False)

class Chats(Base):
    __tablename__ = 'chats'
    type = Column(String, default="dm") # dm / private / public
    chat_username = Column(String, primary_key=True)
    chat_id = Column(BigInteger)
    bot_username = Column(String, ForeignKey('bots.username'), nullable=False)
    bot = relationship('Bots', back_populates='chats')


def get_db():
    DATABASE_URL = "postgresql://"
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def main():
    DATABASE_URL = "postgresql://"
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        pass

if __name__ == "__main__":
    main()