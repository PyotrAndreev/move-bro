from typing import List
from sqlalchemy import ForeignKey
from sqlalchemy import String, Text
from sqlalchemy import Integer
from sqlalchemy import Float
from sqlalchemy import Date, DateTime
from datetime import date, datetime
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_base

from sqlalchemy import create_engine
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker
from TelegramBot.config import config
from TelegramBot.enum_types import *

Base = declarative_base()

class User(Base):
    __tablename__ = "user"

    courier: Mapped["Courier"] = relationship(back_populates="user", cascade="all, delete-orphan")
    comments_to_courier: Mapped[List["Comment_to_Courier"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    packages: Mapped[List["Package"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    notes: Mapped[List["PackageNote"]] = relationship(back_populates="sender")
    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column(String)
    last_name: Mapped[str] = mapped_column(String)
    gender: Mapped[str] = mapped_column(String)
    email: Mapped[str] = mapped_column(String)
    phone: Mapped[str] = mapped_column(String)
    registration_date: Mapped[date] = mapped_column(Date)
    telegram_id: Mapped[int] = mapped_column(Integer)

class Courier(Base):
    __tablename__ = "courier"

    user: Mapped["User"] = relationship(back_populates="courier", )
    my_comments: Mapped[List["Comment_to_Courier"]] = relationship(back_populates="courier", cascade="all, delete-orphan")
    packages: Mapped[List["Package"]] = relationship(back_populates="courier")
    courier_requests: Mapped[List["Courier_Request"]] = relationship(back_populates="courier")

    courier_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.user_id"))
    status: Mapped[CourierStatusEnum] = mapped_column(default=CourierStatusEnum.inactive)
    current_location: Mapped[str] = mapped_column(String, nullable=True)
    last_update: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    overall_rating: Mapped[float] = mapped_column(Float, default=0)
    votes_count: Mapped[int] = mapped_column(Integer, default=0)

class Courier_Request(Base):
    __tablename__ = "courier_request"

    courier: Mapped["Courier"] = relationship(back_populates="courier_requests")
    packages: Mapped[List["Package"]] = relationship(back_populates="courier_request")

    courier_request_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    courier_id: Mapped[int] = mapped_column(ForeignKey("courier.courier_id"), nullable=False)

    shipping_country: Mapped[str] = mapped_column(String)
    shipping_state: Mapped[str] = mapped_column(String, nullable=True)
    shipping_city: Mapped[str] = mapped_column(String)

    delivery_country: Mapped[str] = mapped_column(String)
    delivery_state: Mapped[str] = mapped_column(String, nullable=True)
    delivery_city: Mapped[str] = mapped_column(String)

    comment: Mapped[Text] = mapped_column(Text, nullable=True)

class Comment_to_Courier(Base):
    __tablename__ = "comment_to_courier"

    user: Mapped["User"] = relationship(back_populates="comments_to_courier")
    courier: Mapped["Courier"] = relationship(back_populates="my_comments")

    comment_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.user_id"))
    courier_id: Mapped[int] = mapped_column(ForeignKey("courier.courier_id"))
    creation_date: Mapped[datetime] = mapped_column(DateTime)
    content: Mapped[Text] = mapped_column(Text)

class Package(Base):
    __tablename__ = "package"

    user: Mapped["User"] = relationship(back_populates="packages")
    courier: Mapped["Courier"] = relationship(back_populates="packages")
    courier_request: Mapped["Courier_Request"] = relationship(back_populates="packages")
    comments: Mapped[List["PackageNote"]] = relationship(back_populates="package")
    #replies: Mapped[List["Reply"]] = relationship(back_populates="package")

    package_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("user.user_id"))
    courier_id: Mapped[int] = mapped_column(ForeignKey("courier.courier_id"), nullable=True)
    courier_request_id: Mapped[int] = mapped_column(ForeignKey("courier_request.courier_request_id"), nullable=True)

    recipient_name: Mapped[str] = mapped_column(String)
    recipient_email: Mapped[str] = mapped_column(String, nullable=True)
    recipient_phone: Mapped[str] = mapped_column(String, nullable=True)
    recipient_telegram_id: Mapped[str] = mapped_column(String, nullable=True)

    weight: Mapped[float] = mapped_column(Float)
    length: Mapped[float] = mapped_column(Float)
    width: Mapped[float] = mapped_column(Float)
    height: Mapped[float] = mapped_column(Float)

    cost: Mapped[float] = mapped_column(Float)
    payment_method: Mapped[PaymentMethodEnum] = mapped_column(default=PaymentMethodEnum.tmp)
    payment_date: Mapped[date] = mapped_column(Date, nullable=True)
    purchase_status: Mapped[PaymentStatusEnum] = mapped_column(default=PaymentStatusEnum.uncomplete)

    shipping_country: Mapped[str] = mapped_column(String)
    shipping_state: Mapped[str] = mapped_column(String, nullable=True)
    shipping_city: Mapped[str] = mapped_column(String)
    shipping_street: Mapped[str] = mapped_column(String)
    shipping_house: Mapped[str] = mapped_column(String)
    shipping_postal_code: Mapped[str] = mapped_column(String)

    delivery_country: Mapped[str] = mapped_column(String)
    delivery_state: Mapped[str] = mapped_column(String, nullable=True)
    delivery_city: Mapped[str] = mapped_column(String)
    delivery_street: Mapped[str] = mapped_column(String)
    delivery_house: Mapped[str] = mapped_column(String)
    delivery_postal_code: Mapped[str] = mapped_column(String)

    shipping_date: Mapped[date] = mapped_column(Date, nullable=True)
    preliminary_delivery_date: Mapped[date] = mapped_column(Date, nullable=True)
    package_status: Mapped[PackageStatusEnum] = mapped_column(default=PackageStatusEnum.no_courier)
    current_location: Mapped[str] = mapped_column(String, nullable=True)
    last_update_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)

class PackageNote(Base):
    __tablename__ = "package_note"

    package: Mapped["Package"] = relationship(back_populates="comments")

    package_note_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    package_id: Mapped[int] = mapped_column(ForeignKey("package.package_id"))
    sender_type: Mapped[SenderEnum] = mapped_column(default=SenderEnum.none)
    sender: Mapped["User"] = relationship(back_populates="notes")
    sender_id: Mapped[int] = mapped_column(ForeignKey("user.user_id"), nullable=True)
    creation_date: Mapped[datetime] = mapped_column(DateTime)
    content: Mapped[Text] = mapped_column(Text)
'''class Reply(Base):
    __tablename__ = "replies"
    reply_id = Mapped[int] = mapped_column(primary_key=True)
    reply_comment: Mapped[str] = mapped_column(String)
    creation_date: Mapped[str] = mapped_column(String)
    package_id: Mapped[int] = mapped_column(ForeignKey("packages.package_id"))
    reply_user_id: Mapped[str] = mapped_column(String)

    package: Mapped["Package"] = relationship(back_populates="replies")'''
class Logging(Base):
    __tablename__ = "logging"

    log_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    log_type: Mapped[LogTypeEnum] = mapped_column()
    log_date: Mapped[datetime] = mapped_column(DateTime)
    user_telegram_id: Mapped[int] = mapped_column(Integer)
    user_id: Mapped[int] = mapped_column(Integer)
    log_text: Mapped[str] = mapped_column(String)

class Payments(Base):
    __tablename__ = "payments"

    payment_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    # log_type: Mapped[LogTypeEnum] = mapped_column()
    # log_date: Mapped[datetime] = mapped_column(DateTime)
    # user_telegram_id: Mapped[int] = mapped_column(Integer)
    user_id: Mapped[int] = mapped_column(Integer)
    order_id: Mapped[int] = mapped_column(Integer)
    # log_text: Mapped[str] = mapped_column(String)

def create_database():
    #engine = create_engine('sqlite:///DataBase.db')
    engine = create_engine(config.connection_string.get_secret_value())
    Base.metadata.create_all(engine)
    return engine

def get_db():
    #engine = create_engine('sqlite:///DataBase.db')
    engine = create_engine(config.connection_string.get_secret_value())
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def main():
    engine = create_database()
    with Session(engine) as session:
        pass

if __name__ == "__main__":
    main()