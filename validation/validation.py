from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime
import re
from phonenumbers import phonenumber
from geopy.geocoders import Nominatim

for_naming = r"^[А-ЯЁ][а-яё]*$"


def check_password(value: str,
                   min_length: int = 8,
                   special_chars: bool = True,
                   numbers: bool = True,
                   uppercase: bool = True,
                   lowercase: bool = True) -> bool:
    """ check if the string is strong password or not

    requirements:
        1. At least 8 characters long
        2. At least one uppercase letter
        3. At least one lowercase letter
        4. At least one number
        5. At least one special character
    """
    if len(value) < min_length or \
            (special_chars and len(re.findall(r'[_@$]', value))) < 1 or \
            (numbers and len(re.findall(r'[0-9]', value))) < 1 or \
            (uppercase and len(re.findall(r'[A-Z]', value))) < 1 or \
            (lowercase and len(re.findall(r'[a-z]', value))) < 1:
        return False
    return True


def check_data(val):
    if not isinstance(val, str):
        val = val.split()[0]
        val = datetime.strptime(val, '%Y-%m-%d')
    if not isinstance(val, str) and not not isinstance(val, datetime):
        raise ValueError('Registration date must be a string or a datetime object')


class Address(BaseModel):
    country: str = Field(pattern=for_naming)
    city: str = Field(pattern=for_naming)
    street: str = Field(pattern=for_naming)
    postal_code: int

    @field_validator('country')
    def validate_country(cls, val):
        if not isinstance(val, str):
            raise ValueError('Country must be a string')
        return val.capitalize()

    @field_validator('city')
    def validate_city(cls, val):
        if not isinstance(val, str):
            raise ValueError('City must be a string')
        return val.capitalize()

    @field_validator('street')
    def validate_street(cls, val):
        if not isinstance(val, str):
            raise ValueError('Street must be a string')
        return val.capitalize()

    @field_validator('postal_code')
    def validate_postal_code(cls, val):
        if isinstance(val, int):
            val = str(val)
        russian_pattern = r'^\d{6}$'
        if not isinstance(val, str) or not re.match(russian_pattern, val):
            raise ValueError('Postal code bad format')
        return val


class User(BaseModel):
    first_name: str = Field(pattern=for_naming, alias='FirstName')
    last_name: str = Field(pattern=for_naming, alias='LastName')
    email: EmailStr
    phone: str = phonenumber.PhoneNumber
    registration_date: datetime
    address: Address

    @field_validator('first_name', 'last_name')
    def validate_name(cls, val):
        if not isinstance(val, str) or not val.strip():
            raise ValueError('Name fields cannot be empty')
        return val.capitalize()

    @field_validator('registration_date')
    def validate_registration_date(cls, val):
        check_data(val)
        if val > datetime.today():
            raise ValueError('Registration date cannot be in the future')
        return val


class Payment(BaseModel):
    amount: float
    payment_method: str
    payment_date: datetime
    package: Optional['Package'] = None

    @field_validator('amount')
    def validate_amount(cls, val):
        if not isinstance(val, float):
            raise ValueError('Amount must be a float')
        if val <= 0:
            raise ValueError('Payment amount must be a positive number')
        return val

    @field_validator('payment_method')
    def validate_payment_method(cls, val):
        if not isinstance(val, str):
            raise ValueError('Payment method must be a str')
        return val

    @field_validator('payment_date')
    def validate_payment_data(cls, val):
        check_data(val)
        return val


class Package(BaseModel):
    weight: str = Field(pattern=r'^\d+\skg$', description="Weight in kg format")
    size: str = Field(pattern=r'\d+')
    cost: str = Field(pattern=r'\d+')
    shipping_date: datetime
    delivery_date: datetime
    shipping_address: Address
    delivery_address: Address
    courier: Optional['Courier'] = None
    payment: Optional['Payment'] = None

    @field_validator('shipping_date')
    def validate_shipping_date(cls, val):
        check_data(val)
        return val

    @field_validator('delivery_date')
    def validate_delivery_date(cls, val, values):
        shipping_date = values.get('shipping_date')
        if shipping_date and val >= shipping_date:
            raise ValueError('Delivery date cannot be before shipping date')
        return val


class Courier(BaseModel):
    user: User
    package: Optional[Package] = None  # Optional to prevent circular dependency


# Update forward references after all classes are defined
Package.model_rebuild()
Payment.model_rebuild()


def check_location(address: Address):
    s = address.country + ", " + address.city + ", " + address.street + str(address.postal_code)
    geolocator = Nominatim(user_agent="address_checker")
    locations = geolocator.geocode(s, addressdetails=True, exactly_one=False)
    for location in locations:
        if location.raw['address']['postcode'] == str(address.postal_code):
            return True
    return False
