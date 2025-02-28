from datetime import  date
from typing import List, Optional
from uuid import UUID

from bson import ObjectId
from fastapi_camelcase import CamelModel
from pydantic import EmailStr, Field, constr

from app.models.common.address import Address
from app.models.common.common import LiveTest, YesNo
from app.models.common.country import Country
from app.models.common.data_grid_header_column import DataGridHeaderColumn
from app.models.common.key_fields import KeyField
from app.models.common.province import Province
from app.models.common.py_object_id import PyObjectId
from app.models.common.who_create_data_model import WhoCreateDataModel
from app.models.common.who_update_data_model import WhoUpdateDataModel


class AccAddressModel(Address):
    fax: Optional[constr(max_length=15)]
    email: EmailStr



class SingleAccountantModel(CamelModel):
    acc_title: constr(max_length=50)
    first_name: constr(max_length=30)
    last_name: constr(max_length=30)
    initial: Optional[constr(max_length=3)]
    address: AccAddressModel
    support_access_level_can_manage: YesNo
    start_date: date
    end_date: Optional[date]
    type: LiveTest
    activate_account: bool
    default_accountant: bool
    
    
class AccountantResponse(SingleAccountantModel, WhoCreateDataModel, WhoUpdateDataModel):
    id: PyObjectId = Field(default_factory=PyObjectId)
    
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class AccountantListModel(CamelModel):
    id: Optional[str]
    first_name: str
    last_name: str
    acc_title: str
    email: EmailStr
    post_code: Optional[str]
    city: Optional[str]
    province: Optional[str]
    country: Optional[str]


class AccountantStatusUpdateModels(CamelModel):
    accountant_ids: List[UUID]


class GlobalSearchPayload(CamelModel):
    accountant_search_text: str
    client_search_text: str
    role_id: List[Optional[UUID]]
    resource_search_text: str


class GlobalSearchAccountant(CamelModel):
    id: UUID
    acc_title: str


class GlobalSearchClient(CamelModel):
    id: UUID
    client_identity_no: Optional[str]
    client_name: str
    accountant_id: UUID


class GlobalSearchResources(CamelModel):
    id: UUID
    name1: str
    name2: Optional[str]
    role_name: str
    accountant_id: UUID
    client_id: UUID
    role_id: UUID


class GlobalSearchResponse(CamelModel):
    accountants: List[Optional[GlobalSearchAccountant]]
    clients: List[Optional[GlobalSearchClient]]
    resources: List[Optional[GlobalSearchResources]]


class AccountantListResponseModel(CamelModel):
    page: Optional[int]
    size: Optional[int]
    total: Optional[int]
    items: Optional[List[AccountantListModel]]
    key_field: Optional[List[KeyField]]
    header_columns: Optional[List[DataGridHeaderColumn]]
