from typing import Optional

from bson import ObjectId
from fastapi_camelcase import CamelModel
from pydantic import Field, conint, constr

from app.models.common.common import ActiveInactive
from app.models.common.py_object_id import PyObjectId
from app.models.common.who_create_data_model import WhoCreateDataModel
from app.models.common.who_update_data_model import WhoUpdateDataModel


class ClientBank(CamelModel):
    client_id: Optional[str]
    name: Optional[constr(max_length=50)]
    account_no: Optional[constr(max_length=18)]
    branch_transit_number: Optional[conint(ge = 5)]
    bank_financial_no: Optional[conint(ge = 4)]
    primary_account: Optional[bool]
    status: ActiveInactive = Field(default=ActiveInactive.INACTIVE)
    
    
class ClientBankResponse(ClientBank, WhoCreateDataModel, WhoUpdateDataModel):
    
    id: PyObjectId = Field(default_factory=PyObjectId)
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}