# from logging import Logger
from fastapi.encoders import jsonable_encoder
from app.database.rbac.oauth import OAuthDatabase
from app.database.rbac.user import AuthenticationsDatabase
from app.models.common.common import ResponseMessage
from app.models.common.logger import Logger
from datetime import timedelta
from random import randrange
import datetime
import hashlib
from app.models.rbac.user_authentication import ForgotPasswordPayload, UserInLogin, UserOauth, UserOut, UserRegisterPayload, UserRegistrationOut, VerifyEmailPayload



class AuthenticationManager():
    def __init__(self) -> None:
        self.authentication_database = AuthenticationsDatabase()
        self.oauth_database = OAuthDatabase()
        self.logger = Logger()


    async def register(self, payload: UserRegisterPayload):
        where_clouse = {"email": payload.email}
        email_already_exist = await self.authentication_database.get_by_whereclouse(where_clouse)
        if email_already_exist:
            # return ResponseMessage(success=False, message=f"Email already Exist")
            return {"success":False, "message":f"Email already Exist"}
        payload = jsonable_encoder(payload)
        payload_data = UserRegistrationOut(**payload, is_super_status=0, two_factor_auth=False, password="112233445566")
        response = await self.authentication_database.register(payload_data)
        return response
    
    async def login(self, payload: dict):
        where_clouse = {"email": payload.get("email"), "password": payload.get("password")}
        user_already_exist = await self.authentication_database.get_by_whereclouse(where_clouse)
        if not user_already_exist:
            return ResponseMessage(success=False, message="Email or Password is incorrect")
        user_already_exist["userId"] = str(user_already_exist["_id"])
        del user_already_exist["_id"]
        access_token = self.generate_code()
        payload_data = UserOauth(email=payload.get("email"), access_token=access_token, user_id=str(user_already_exist["userId"]), created_date=datetime.datetime.now(),
                                 expires_on=datetime.datetime.now() + datetime.timedelta(days=1), user_role= user_already_exist["isSuperStatus"])
        
        where_clouse = {"email": payload.get("email"), "userId": str(user_already_exist["userId"])}
        oauth_data = await self.oauth_database.get_by_whereclouse(where_clouse)
        if oauth_data:
            response = await self.oauth_database.updated_user_detail(payload_data)
            response["user"] = user_already_exist
            response["user"]["accessToken"] = response["accessToken"]
            response["user"]["expiresOn"] = response["expiresOn"]
            response["user"]["userRole"] = response["userRole"]
            return response
        response = await self.oauth_database.login(payload_data)
        response["user"] = user_already_exist
        return response
    
    async def get_email_link_key(self, link_key: str):
        where_clouse = {"randomKey": link_key}
        api_response = await self.authentication_database.get_by_whereclouse(where_clouse)
        return api_response
    
    async def verify_email(self, payload: VerifyEmailPayload):
        where_clouse = {"email": payload.email}
        api_response = await self.authentication_database.get_by_whereclouse(where_clouse)
        return api_response
    
    async def set_password(self, payload: ForgotPasswordPayload):
        where_clouse = {"randomKey": payload.random_key}
        api_response = await self.authentication_database.get_by_whereclouse(where_clouse)

        if api_response:
            api_response["password"] = payload.confirm_new_password
            payload_data = UserRegistrationOut(**api_response, is_super_status= 0, two_factor_auth=False)
            response = await self.authentication_database.updated_user_password(where_clouse, payload_data)

        return api_response
    
    async def updated_with_email(self, payload: dict):
        where_clouse = {"email": payload.get("email")}
        email_already_exist = await self.authentication_database.get_by_whereclouse(where_clouse)
        if not email_already_exist:
            # return ResponseMessage(success=False, message=f"Email already Exist")
            return {"success":False, "message":f"User email not Exist"}
        email_already_exist["randomKey"] = payload.get("random_key")
        response = await self.authentication_database.updated_user_detail(email_already_exist)
        return response
    

    def generate_code(extra_days=1, sha_string=False):

        if not sha_string:
            sha_string = str(datetime.datetime.now() + datetime.timedelta(days=1))
            sha_string = sha_string + str(randrange(10000000, 99999999))

        # sha1_string = hashlib.sha1(b''+str.encode(sha_string))
        sha256_hash = hashlib.sha256(sha_string.encode('utf-8'))
        code = sha256_hash.hexdigest()[:40]

        return code