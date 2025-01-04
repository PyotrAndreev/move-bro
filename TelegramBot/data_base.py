from typing import List
from sqlalchemy import ForeignKey
from sqlalchemy import String, Text
from sqlalchemy import Integer
from sqlalchemy import BigInteger
from sqlalchemy import Float
from sqlalchemy import Date, DateTime
from datetime import date, datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker

from TelegramBot.enum_types import *

Base = declarative_base()

class User(Base):
    __tablename__ = "user"

    courier: Mapped["Courier"] = relationship(back_populates="user", cascade="all, delete-orphan")
    comments_to_courier: Mapped[List["Comment_to_Courier"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    packages: Mapped[List["Package"]] = relationship(back_populates="user", cascade="all, delete-orphan")

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

    courier_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.user_id"))
    status: Mapped[CourierStatusEnum] = mapped_column(default=CourierStatusEnum.inactive, create_type=False)
    current_location: Mapped[str] = mapped_column(String)
    last_update: Mapped[datetime] = mapped_column(DateTime)
    overall_rating: Mapped[float] = mapped_column(Float, default=0)
    votes_count: Mapped[int] = mapped_column(Integer, default=0)

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
    comments: Mapped[List["Package_Note"]] = relationship(back_populates="package")

    package_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("user.user_id"))
    courier_id: Mapped[int] = mapped_column(ForeignKey("courier.courier_id"), nullable=True)

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
    package_status: Mapped[PackageStatusEnum] = mapped_column(default=PackageStatusEnum.not_brought)
    current_location: Mapped[str] = mapped_column(String, nullable=True)
    last_update_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)

class Package_Note(Base):
    __tablename__ = "package_note"

    package: Mapped["Package"] = relationship(back_populates="comments")

    package_note_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    package_id: Mapped[int] = mapped_column(ForeignKey("package.package_id"))
    sender: Mapped[SenderEnum] = mapped_column(default=SenderEnum.none)
    creation_date: Mapped[datetime] = mapped_column(DateTime)
    content: Mapped[Text] = mapped_column(Text)

def create_database():
    engine = create_engine('sqlite:///DataBase.db')
    Base.metadata.create_all(engine)
    return engine

def get_db():
    engine = create_engine('sqlite:///DataBase.db')
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
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