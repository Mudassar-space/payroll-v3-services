from enum import Enum
from typing import Optional
from fastapi_camelcase import CamelModel
from pydantic import conint, constr


class City(CamelModel):
    id: Optional[str]
    name: constr(min_length=1, max_length=60)
    short_code: constr(max_length=4)

class Province(CamelModel):
    id: Optional[str]
    name: constr(min_length=1, max_length=50)
    short_code: constr(min_length=1, max_length=2)

class Country(CamelModel):
    id: Optional[str]
    name: constr(min_length=1, max_length=60)
    short_code: constr(min_length=1, max_length=3)

class ResponseMessage(CamelModel):
    success: bool
    message: str

class APIResponse(CamelModel):  # pylint: disable=too-few-public-methods
    status: bool
    message: str


class UnauthorizedResponse(CamelModel):
    detail: str

class ErrorMessages(Enum):
    server_error = "Internal Server Error."
    connection_error = "Master Data API connection not established."
    server_busy_error = "Server is too busy at the moment, please retry in 15 minutes."
    rbac_connection_error = "RBAC API connection not established."
    record_not_found = "Record not found."
    unauthorized_access = "You are not authorized to access this resource. please contact administrator for further details."


class YesNo(int, Enum):
    NO = 100
    YES = 200

class LiveTest(int, Enum):
    LIVE = 100
    TEST = 200

class SelfOrSimplePay(int, Enum):
    SELF_MANAGED = 100
    SIMPLEPAY = 200

class ActiveInactive(int, Enum):
    ACTIVE = 100
    INACTIVE = 200

class YesNoPending(int, Enum):
    NO =100
    PENDING_APPROVAL = 200
    YES = 300

class DaysEnum(int, Enum):
    DAYS_3 = 100
    DAYS_4 = 200
    DAYS_5 = 300

class ApOrCompanyAccount(int, Enum):
    AP_ACCOUNT =100
    COMPANY_ACCOUNT = 200

class TransactionMethod(int, Enum):
    CREDIT_CARD =100
    PRE_AUTHORIZED_DEBIT = 200
    WIRE_TRANSFER = 300

class Gender(int, Enum):
    FEMALE =100
    MALE = 200

class Languages(int, Enum):
    ENGLISH = 100
    FRENCH = 200

class BankSplit(int, Enum):
    FIXED_AMOUNT = 100
    NO_SPLIT = 200
    PERCENTAGE = 300

class PayMethod(int, Enum):
    CHEQUE = 100
    DIRECT_DEPOSIT = 200


class EmployeeStatus(int, Enum):
    ACTIVE = 100
    INACTIVE = 200
    REHIRED = 300
    TERMINATED = 400
    
    
class DeductionType(int, Enum):
    ANNUAL_DEDUCTIONS = 100
    DEDUCTION_BY_COURT_ORDER  = 200
    RPP = 300
    UNION_DUES = 400
    
    
class DEDUCTION_FROM(int, Enum):
    GROSS = 100
    NET_PAY = 200
    
    
class DEDUCTION_METHOD(int, Enum):
    AMOUNT = 100
    PERCENTAGE_OF_GROSS_CASH_EARNINGS = 200
    PERCENTAGE_OF_GROSS_ONLY = 300
    PERCENTAGE_OF_TOTAL_GROSS = 400
    
    
class PAYMENT_TYPE(int, Enum):
    AMOUNT = 100
    HOURS = 200
    PERCENTAGE_OF_GROSS_ONLY = 300
    
    
class HOURLY_RATE(int, Enum):
    CUSTOM_RATE = 100
    FULL_REGULAR_RATE = 200
    HALF_REGULAR_RATE = 300
    REGULAR_RATE = 400
    