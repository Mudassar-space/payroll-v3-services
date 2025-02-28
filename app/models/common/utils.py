from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from app.models.common.common import APIResponse, ErrorMessages
from app.models.rbac.user_authentication import UserTokenPayload


def is_admin_user(token_payload: UserTokenPayload):
    return token_payload.user_role == 1

def get_unauthorized_response():
    forbidden_response = APIResponse(status = False, message=ErrorMessages.UNAUTHORIZED_ACCESS.value)
    return JSONResponse(status_code = status.HTTP_403_FORBIDDEN, content = jsonable_encoder(forbidden_response))
