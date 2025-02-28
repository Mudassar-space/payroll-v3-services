from datetime import datetime
from typing import List, Optional
from bson import ObjectId
from fastapi_camelcase import CamelModel
from pydantic import Field, conint, constr

from app.models.common.common import Country
from app.models.common.data_grid_header_column import DataGridHeaderColumn
from app.models.common.key_fields import KeyField
from app.models.common.py_object_id import PyObjectId



class ProvinceRequestPayload(Country):
    country: Optional[str]




class ProvinceResponsePayload(ProvinceRequestPayload):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId)


class ProvinceUpdateResponse(ProvinceRequestPayload):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId)
    created_by: Optional[constr(min_length=5, max_length=50)]
    created_by_external_id: Optional[conint(gt=0)]
    created_on: Optional[datetime]
    updated_by: Optional[constr(min_length=5, max_length=50)]
    updated_on: Optional[datetime]


class ProvinceListResponse(CamelModel):
    page: Optional[int]
    size: Optional[int]
    total: Optional[int]
    items: Optional[List[ProvinceResponsePayload]]
    key_field: Optional[List[KeyField]]
    header_columns: Optional[List[DataGridHeaderColumn]]

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class ProvinceDdlResponsePayload(CamelModel):
    short_code: Optional[str]
    value: Optional[str]
    label: Optional[str]
class ProvinceDdlListResponse(CamelModel):
    total: Optional[int]
    items: Optional[List[ProvinceDdlResponsePayload]]

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
