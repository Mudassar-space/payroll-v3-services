from datetime import datetime
from typing import List, Optional
from bson import ObjectId
from fastapi_camelcase import CamelModel
from pydantic import Field, confloat, conint, constr, root_validator
from app.models.common.py_object_id import PyObjectId
from bson.errors import InvalidId

from app.models.common.common import DEDUCTION_FROM, DEDUCTION_METHOD, HOURLY_RATE, PAYMENT_TYPE, Country, DeductionType, YesNo
from app.models.common.data_grid_header_column import DataGridHeaderColumn
from app.models.common.key_fields import KeyField
from app.models.common.py_object_id import PyObjectId
from app.models.common.who_create_data_model import WhoCreateDataModel
from app.models.common.who_update_data_model import WhoUpdateDataModel



class EarningRequestPayload(CamelModel):
    client_id:str = Field(default="67beac5f8b7d64c58c15b258")
    label: constr(max_length=25)
    show_in_payroll: YesNo  = YesNo.YES._value_
    earning_type: Optional[str]
    payment_type: PAYMENT_TYPE = PAYMENT_TYPE.AMOUNT._value_
    hourly_rate: Optional[HOURLY_RATE] = HOURLY_RATE.REGULAR_RATE._value_
    rate: Optional[float]
    deduct_cpp_qpp:YesNo  = YesNo.YES._value_
    deduct_ei:YesNo  = YesNo.YES._value_
    deduct_federal_tax:YesNo  = YesNo.YES._value_
    deduct_provincial_tax:YesNo  = YesNo.YES._value_
    deduct_qpip:YesNo  = YesNo.YES._value_
    calculate_eht_ontario:YesNo  = YesNo.YES._value_
    calculate_wsib_wcb:YesNo  = YesNo.YES._value_
    deduct_csst:YesNo  = YesNo.YES._value_
    deduct_hsf:YesNo  = YesNo.YES._value_
    calculate_vocation_pay:YesNo  = YesNo.YES._value_
    calculate_holiday_pay:YesNo  = YesNo.YES._value_
    exclude_from_t4_box_14:YesNo  = YesNo.YES._value_
    exclude_from_rl1_box_a:YesNo  = YesNo.YES._value_
    gst_hst_include: YesNo  = YesNo.YES._value_
    max_ytd: Optional[confloat(le=99999999.99)]
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


class EarningResponsePayload(EarningRequestPayload,WhoCreateDataModel,WhoUpdateDataModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId)
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class EarningListModel(CamelModel):
    label: constr(max_length=25)
    show_in_payroll: YesNo  = YesNo.YES._value_
    earning_type: Optional[str]
    payment_type: PAYMENT_TYPE = PAYMENT_TYPE.AMOUNT._value_
    hourly_rate: Optional[HOURLY_RATE] = HOURLY_RATE.REGULAR_RATE._value_
    max_ytd: Optional[confloat(le=99999999.99)]
    t4_code: Optional[str]
    rl1_code: Optional[str]
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId)
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class EarningListResponseModel(CamelModel):
    page: Optional[int]
    size: Optional[int]
    total: Optional[int]
    items: Optional[List[EarningListModel]]
    key_field: Optional[List[KeyField]]
    header_columns: Optional[List[DataGridHeaderColumn]]