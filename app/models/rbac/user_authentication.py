from typing import Optional
from fastapi_camelcase import CamelModel
from datetime import datetime
from pydantic import EmailStr, Field, constr


class Register(CamelModel):
    first_name: str
    last_name: str # constr(min_length=1, max_length=45) # type: ignore
    email: EmailStr
    timezone: Optional[str] # constr(min_length=1, max_length=100) # type: ignore

class UserRegisterPayload(Register):
    random_key: Optional[str]
    source: Optional[str]

class VerifyEmailPayload(CamelModel):
    """ Model for verify email payload """
    email: EmailStr

class ForgotPasswordPayload(CamelModel):
    """ Model for Forgot Password payload """
    random_key: str
    new_password: constr(min_length=8, max_length=20)
    confirm_new_password: constr(min_length=8, max_length=20)


class UserOut(CamelModel):
    first_name: constr(max_length=45)
    last_name: constr(max_length=45)
    email: EmailStr
    phone: Optional[str]
    country_code: Optional[str]
    two_factor_auth: bool
    is_super_status: int
    

class UserRegistrationOut(UserOut):
    password: Optional[constr(min_length=8, max_length=20)]

class UserRegisterResponsePayload(CamelModel):
    created: bool
    user_created: bool
    verify_key: str
    status: str
    message: str

class UserInLogin(CamelModel):
    email: EmailStr
    password: constr(min_length=8, max_length=20)

class UserOutLogin(CamelModel):
    status: bool
    message: str
    user: UserOut
    token: str


class UserOauth(CamelModel):
    email: EmailStr
    access_token: str
    created_date: Optional[datetime]
    expires_on: datetime
    user_id: str
    user_role: int


class UserTokenPayload(CamelModel):
    access_token: str
    expires: float
    user: UserOauth
    user_email: str
    user_id: str
    user_role: int



