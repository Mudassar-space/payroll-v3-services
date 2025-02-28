
from fastapi_camelcase import CamelModel


class ResponseMessage(CamelModel):
    success: bool
    message: str
