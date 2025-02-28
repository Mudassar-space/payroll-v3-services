from datetime import datetime, date
from typing import List, Optional
from uuid import UUID

from bson import ObjectId
from fastapi_camelcase import CamelModel
from pydantic import EmailStr, Field, conint, constr

from app.models.common.address import Address

from app.models.common.common import ActiveInactive, ApOrCompanyAccount, BankSplit, DaysEnum, Gender, Languages, PayMethod, Province, SelfOrSimplePay, TransactionMethod, YesNo, YesNoPending
from app.models.common.data_grid_header_column import DataGridHeaderColumn
from app.models.common.dropdown import DropDown
from app.models.common.key_fields import KeyField
from app.models.common.py_object_id import PyObjectId
from app.models.common.who_create_data_model import WhoCreateDataModel
from app.models.common.who_update_data_model import WhoUpdateDataModel



class EmployeeAddressModel(Address):
    zip_code: Optional[str]
    phone2: Optional[str]
    website: Optional[constr(max_length=50)]
    stub_email_from: EmailStr

class EmployeeStub(CamelModel):
    stub_language: Languages
    email_stub: YesNo
    print_hourly_rate_on_stub: YesNo
    stub_notes: Optional[constr(max_length=100)]

class EmployeeBank(CamelModel):
    account_1_name: Optional[constr(max_length=50)]
    account_no: Optional[constr(max_length=18)]
    branch_transit_number: Optional[constr(max_length=5)]
    bank_financial_no: Optional[constr(max_length=4)]
    account_2_name: Optional[constr(max_length=50)]
    account_2_no: Optional[constr(max_length=18)]
    branch_transit_number_for_account_2: Optional[constr(max_length=5)]
    bank_financial_no_for_account_2: Optional[constr(max_length=4)]
    split: BankSplit
    percenage_per_dollor_in_account_1: Optional[int]

class EmployeePayroll(CamelModel):
    pay_frequency: Optional[constr(max_length=50)]
    date_of_hire: date
    pay_method: PayMethod
    province_of_employment: Province
    date_of_termination: date
    include_in_t4_or_rl1: YesNo

class EmployeeReuestPayload(CamelModel):
    employee_id: Optional[str]
    client_id: str
    first_name: str
    last_name: str
    initial: Optional[str]
    gender: Gender
    date_of_birth: date
    social_insurance_number: str
    address: Address
    employee_setub: EmployeeStub
    employee_bank: EmployeeBank
    employee_payroll: EmployeePayroll

    
class EmployeeResponse(EmployeeReuestPayload, WhoCreateDataModel, WhoUpdateDataModel):
    id: PyObjectId = Field(default_factory=PyObjectId)
    
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

        
class EmployeeListResponseModel(CamelModel):
    page: Optional[int]
    size: Optional[int]
    total: Optional[int]
    items: Optional[List[EmployeeReuestPayload]]
    key_field: Optional[List[KeyField]]
    header_columns: Optional[List[DataGridHeaderColumn]]
    
    
class AssignEmployees(CamelModel):
    client_id: str
    employee_id: str
    department_id:str
    designation_id: str
    team_id:str