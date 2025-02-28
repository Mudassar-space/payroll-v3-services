from typing import Optional

from fastapi_camelcase import CamelModel
from pydantic import conint, constr


class Country(CamelModel):
    id: Optional[conint(gt=0)]
    name: constr(min_length=1, max_length=60)
    short_code: constr(min_length=1, max_length=3)
