from typing import List, Optional
from bson import ObjectId
from fastapi_camelcase import CamelModel
from datetime import datetime
from pydantic import  Field

from app.models.common.data_grid_header_column import DataGridHeaderColumn
from app.models.common.key_fields import KeyField
from app.models.common.py_object_id import PyObjectId


class UserRolesRequestModel(CamelModel):
    role_name: str   
    user_type: int
    owner_role: int
    application_id: str
    created_by_id: Optional[str]
    deleted: int
    created_on: datetime

class UserRolesResponseModel(UserRolesRequestModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId)


class UserRolesListResponse(CamelModel):
    page: Optional[int]
    size: Optional[int]
    total: Optional[int]
    items: Optional[List[UserRolesResponseModel]]
    key_field: Optional[List[KeyField]]
    header_columns: Optional[List[DataGridHeaderColumn]]

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
