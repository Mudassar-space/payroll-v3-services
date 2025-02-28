from typing import Union

from fastapi_camelcase import CamelModel


class DDLEntity(CamelModel):
    label: str
    value: str
