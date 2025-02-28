from typing import Optional

from fastapi_camelcase import CamelModel


class DropDown(CamelModel):
    label: Optional[str]
    value: Optional[str]


class DropDownMax(DropDown):
    code: Optional[str]