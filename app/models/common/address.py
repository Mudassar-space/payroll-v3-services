from typing import  Optional
from fastapi_camelcase import CamelModel
from pydantic import EmailStr, constr
from app.models.common.common import Country, Province


class Address(CamelModel):
    country_type: Optional[bool]
    country: Optional[Country]
    province: Optional[Province]
    states: Optional[Province]
    address_line1: constr(max_length=100)
    city: constr(max_length=30)
    post_code: Optional[constr(max_length=10)]
    phone: str
    