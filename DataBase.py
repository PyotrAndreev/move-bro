from typing import List
from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import Integer
from sqlalchemy import Float
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Session

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String)
    last_name: Mapped[str] = mapped_column(String)
    email: Mapped[str] = mapped_column(String)
    phone: Mapped[int] = mapped_column(Integer)
    registration_date: Mapped[str] = mapped_column(String)

    address: Mapped["Address"] = relationship(back_populates="users")
    is_courier: Mapped["Courier"] = relationship(back_populates="users")

class Courier(Base):
    __tablename__ = "couriers"

    courier_id: Mapped[int] = mapped_column(primary_key=True)
    status: Mapped[str] = mapped_column(String)
    current_location: Mapped[str] = mapped_column(String)
    rating: Mapped[float] = mapped_column(Float)
    comments: Mapped[str] = mapped_column(String)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"))
    user: Mapped["User"] = relationship(back_populates="couriers")

    package_id: Mapped[int] = mapped_column(ForeignKey("packages.package_id"))
    package: Mapped["Package"] = relationship(back_populates="couriers")

class Address(Base):
    __tablename__ = "addresses"

    address_id: Mapped[int] = mapped_column(primary_key=True)
    country: Mapped[str] = mapped_column(String)
    state: Mapped[str] = mapped_column(String)
    city: Mapped[str] = mapped_column(String)
    street: Mapped[str] = mapped_column(String)
    postal_code: Mapped[int] = mapped_column(Integer)

class Package(Base):
    __tablename__ = "packages"

    package_id: Mapped[int] = mapped_column(primary_key=True)
    weight: Mapped[str] = mapped_column(String)
    size: Mapped[str] = mapped_column(String)
    cost: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String)
    shipping_date: Mapped[str] = mapped_column(String)
    delivery_date: Mapped[str] = mapped_column(String)

    shipping_address: Mapped["Address"] = relationship(back_populates="packages")
    delivery_address: Mapped["Address"] = relationship(back_populates="packages")
    courier: Mapped["Courier"] = relationship(back_populates="packages")
    reports: Mapped[List["Report"]] = relationship(back_populates="packages")
    track: Mapped["Tracking"] = relationship(back_populates="packages")
    payment: Mapped["Payment"] = relationship(back_populates="packages")

class Report(Base):
    __tablename__ = "reports"

    report_id: Mapped[int] = mapped_column(primary_key=True)
    report_content: Mapped[str] = mapped_column(String)
    creation_date: Mapped[str] = mapped_column(String)
    type: Mapped[str] = mapped_column(String)

    package_id: Mapped[int] = mapped_column(ForeignKey("packages.package_id"))
    package: Mapped["Package"] = relationship(back_populates="reports")

class Tracking(Base):
    __tablename__ = "trackings"

    tracking_id: Mapped[int] = mapped_column(primary_key=True)
    status: Mapped[str] = mapped_column(String)
    time_start: Mapped[str] = mapped_column(String)
    time_end: Mapped[str] = mapped_column(String)
    comment: Mapped[str] = mapped_column(String)

    package_id: Mapped[int] = mapped_column(ForeignKey("packages.package_id"))
    package: Mapped["Package"] = relationship(back_populates="trackings")

class Payment(Base):
    __tablename__ = "payments"

    payment_id: Mapped[int] = mapped_column(primary_key=True)
    amount: Mapped[float] = mapped_column(Float)
    payment_method: Mapped[str] = mapped_column(String)
    payment_date: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String)

    package_id: Mapped[int] = mapped_column(ForeignKey("packages.package_id"))
    package: Mapped["Package"] = relationship(back_populates="payments")

def create_database():
    engine = create_engine('sqlite:///DataBase.db')
    Base.metadata.create_all(engine)
    return engine

def main():
    engine = create_database()
    with Session(engine) as session:
        pass

if __name__ == "__main__":
    main()