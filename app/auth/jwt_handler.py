""" JWT token handler written here"""
import time
import json
from jwcrypto import jwt
from fastapi import status
from app.database.rbac.oauth import OAuthDatabase
from app.config.config import ( JWT_KEY,
    JWT_TOKEN_EXPIRE_MINUTES,
    JWT_ALGORITHM, JWT_HEADER_ALGORITHM,
    JWT_HEADER_ENCODING
)
from app.database.rbac.user import AuthenticationsDatabase


def generate_jwt_token(data: dict) -> str:
    """
    Generate jwt token from the data.
    :param data:
    :return:
    """
    to_encode = data.copy()
    to_encode.update({"expires": time.time() + JWT_TOKEN_EXPIRE_MINUTES})
    encode_token = jwt.JWT(
        header={"alg": JWT_ALGORITHM},
        claims=to_encode)
    encode_token.make_signed_token(JWT_KEY)
    token = jwt.JWT(header={"alg": JWT_HEADER_ALGORITHM,
                            "enc": JWT_HEADER_ENCODING},
                    claims=encode_token.serialize())
    token.make_encrypted_token(JWT_KEY)
    return token.serialize()


async def validate_token(token: str) -> dict:
    """
    Validate the provided token by decrypted and validate the access key from the RBAC
    :param token:
    :return:
    """
    try:
        encode_token = jwt.JWT(key=JWT_KEY, jwt=token)
        payload = json.loads(jwt.JWT(key=JWT_KEY, jwt=encode_token.claims).claims)
        where_clouse = {"accessToken": payload.get("access_token")}
        verify_access_token = await OAuthDatabase.get_by_whereclouse_data(where_clouse)
        if not verify_access_token:
            raise ValueError
        return payload
    except ValueError:
        return {}
