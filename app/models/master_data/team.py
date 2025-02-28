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



class TeamRequestPayload(CamelModel):
    team_label: constr(min_length=1, max_length=50)
    notes: Optional[constr(min_length=1, max_length=100)]




class TeamResponsePayload(TeamRequestPayload,WhoCreateDataModel,WhoUpdateDataModel):
    client_id:Optional[str]
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId)
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class TeamListModel(CamelModel):
    team_label: Optional[str]
    notes: Optional[str]
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId)
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class TeamListResponseModel(CamelModel):
    page: Optional[int]
    size: Optional[int]
    total: Optional[int]
    items: Optional[List[TeamListModel]]
    key_field: Optional[List[KeyField]]
    header_columns: Optional[List[DataGridHeaderColumn]]