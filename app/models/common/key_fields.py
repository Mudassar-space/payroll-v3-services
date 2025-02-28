from typing import Optional

from fastapi_camelcase import CamelModel


class KeyField(CamelModel):
    """ Key Field Type model """
    field: Optional[str]
    template_url: Optional[str]
