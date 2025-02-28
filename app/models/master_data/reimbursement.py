from datetime import datetime
from typing import List, Optional
from bson import ObjectId
from fastapi_camelcase import CamelModel
from pydantic import Field, confloat, conint, constr, root_validator
from bson.errors import InvalidId

from app.models.common.common import DEDUCTION_FROM, DEDUCTION_METHOD, Country, DeductionType, YesNo
from app.models.common.data_grid_header_column import DataGridHeaderColumn
from app.models.common.key_fields import KeyField
from app.models.common.py_object_id import PyObjectId
from app.models.common.who_create_data_model import WhoCreateDataModel
from app.models.common.who_update_data_model import WhoUpdateDataModel



class ReimbursementRequestPayload(CamelModel):
    client_id: str = Field(default="67beac5f8b7d64c58c15b258")
    label: constr(max_length=25)
    show_in_payroll: YesNo  = YesNo.YES._value_
    t4_code: Optional[str]
    rl1_code: Optional[str]
    
    @root_validator(pre=False)
    def validate_client_id(cls, value):
        client_id = value["client_id"]
        if client_id is not None:
            try:
                id = PyObjectId(client_id)
                return value
            except InvalidId as e:
                raise ValueError(f"client id '{client_id}' is invalid.")


class ReimbursementResponsePayload(ReimbursementRequestPayload,WhoCreateDataModel,WhoUpdateDataModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId)
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class ReimbursementListModel(CamelModel):
    label: constr(max_length=25)
    show_in_payroll: YesNo  = YesNo.YES._value_
    t4_code: Optional[str]
    rl1_code: Optional[str]
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId)
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class ReimbursementListResponseModel(CamelModel):
    page: Optional[int]
    size: Optional[int]
    total: Optional[int]
    items: Optional[List[ReimbursementListModel]]
    key_field: Optional[List[KeyField]]
    header_columns: Optional[List[DataGridHeaderColumn]]