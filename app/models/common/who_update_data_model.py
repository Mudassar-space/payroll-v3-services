from datetime import datetime
from typing import Optional

from fastapi_camelcase import CamelModel
from pydantic import EmailStr, conint, constr


class WhoUpdateDataModel(CamelModel):
    updated_by_email: Optional[EmailStr]
    updated_by_external_id: Optional[constr(min_length=1, max_length=40)]
    updated_at: Optional[datetime]
