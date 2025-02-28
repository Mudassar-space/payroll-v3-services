from datetime import datetime
from typing import Optional

from fastapi_camelcase import CamelModel
from pydantic import EmailStr, constr


class WhoCreateDataModel(CamelModel):
    created_by_email: Optional[EmailStr]
    created_by_external_id:Optional[constr(min_length=1, max_length=40)]
    created_at: Optional[datetime]
