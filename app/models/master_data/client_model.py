from datetime import datetime, date
from typing import List, Optional
from uuid import UUID

from bson import ObjectId
from fastapi_camelcase import CamelModel
from pydantic import EmailStr, Field, constr

from app.models.common.address import Address

from app.models.common.common import ActiveInactive, ApOrCompanyAccount, DaysEnum, SelfOrSimplePay, TransactionMethod, YesNo, YesNoPending
from app.models.common.data_grid_header_column import DataGridHeaderColumn
from app.models.common.dropdown import DropDown
from app.models.common.key_fields import KeyField
from app.models.common.py_object_id import PyObjectId
from app.models.common.who_create_data_model import WhoCreateDataModel
from app.models.common.who_update_data_model import WhoUpdateDataModel



class ClientAddressModel(Address):
    zip_code: Optional[str]
    phone2: Optional[str]
    website: Optional[constr(max_length=50)]
    stub_email_from: EmailStr


class ClientReuestPayload(CamelModel):
    # id: Optional[str]
    accountant_id: Optional[str]
    company_id: Optional[str]
    legal_name:constr(max_length=100)
    operating_name:constr(max_length=100)
    address: ClientAddressModel
    system_alerts_from: EmailStr
    toll_free: Optional[int]
    cra_business_no: Optional[constr(max_length=15)]
    schedule_start_date: date

class ClientSuperUserReuestPayload(ClientReuestPayload, WhoCreateDataModel, WhoUpdateDataModel):
    transaction_method: TransactionMethod
    is_direct_deposit_required: YesNo
    remittance_management: SelfOrSimplePay
    billing_start_date: date
    billing_status: ActiveInactive
    support_access_level_can_manager: YesNo
    web_r_o_e_managed_by_simplepay: YesNoPending
    direct_deposit_processing: SelfOrSimplePay
    direct_deposit_cycle: DaysEnum
    journal_code: Optional[constr(max_length=10)]
    invoice_deduction: ApOrCompanyAccount
    show_accounting_to_company: YesNo
    activate_account: YesNo



    
    
class ClientResponse(ClientReuestPayload, WhoCreateDataModel, WhoUpdateDataModel):
    id: PyObjectId = Field(default_factory=PyObjectId)
    
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

        
class ClientListResponseModel(CamelModel):
    page: Optional[int]
    size: Optional[int]
    total: Optional[int]
    items: Optional[List[ClientReuestPayload]]
    key_field: Optional[List[KeyField]]
    header_columns: Optional[List[DataGridHeaderColumn]]