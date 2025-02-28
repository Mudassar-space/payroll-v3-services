from datetime import datetime
from typing import List, Optional
from bson import ObjectId
from fastapi_camelcase import CamelModel
from pydantic import Field, conint, constr

from app.models.common.common import Country
from app.models.common.data_grid_header_column import DataGridHeaderColumn
from app.models.common.key_fields import KeyField
from app.models.common.py_object_id import PyObjectId
from app.models.common.who_create_data_model import WhoCreateDataModel
from app.models.common.who_update_data_model import WhoUpdateDataModel



class PayrollFrequenciesRequestPayload(CamelModel):
    label: str



class PayrollFrequenciesResponsePayload(PayrollFrequenciesRequestPayload,WhoCreateDataModel,WhoUpdateDataModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId)
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class PayrollFrequenciesListModel(CamelModel):
    label: Optional[str]
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId)
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class PayrollFrequenciesListResponseModel(CamelModel):
    page: Optional[int]
    size: Optional[int]
    total: Optional[int]
    items: Optional[List[PayrollFrequenciesListModel]]
    key_field: Optional[List[KeyField]]
    header_columns: Optional[List[DataGridHeaderColumn]]