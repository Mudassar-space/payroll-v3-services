"""
Bearer token verification process written here
"""
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.security.utils import get_authorization_scheme_param

from .jwt_handler import validate_token


class JWTAuthentication(HTTPBearer):
    """
    Class to authenticate the request
    """
    def __init__(self, auto_error: bool = True):
        """
        :param auto_error:
        """
        super(JWTAuthentication, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        """
        verify the token from the request header
        :param request:
        :return:
        """

        authorization: str = request.headers.get("Authorization")
        scheme, credentials = get_authorization_scheme_param(authorization)
        if not (authorization and scheme and credentials) and self.auto_error:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication credentials were not provided."
            )
        if scheme.lower() != "bearer" and self.auto_error:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials.",
            )

        credentials =  HTTPAuthorizationCredentials(scheme=scheme, credentials=credentials)

        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication scheme.")

            payload = await validate_token(credentials.credentials)

            if not payload.get("access_token"):
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid partner token or expired token.")
            return payload
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization code.")
