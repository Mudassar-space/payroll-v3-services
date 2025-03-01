
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
# from requests_async.exceptions import ConnectionError as ConnectionException

from app.constants.constants import AUTH_LINK, IP, LINK_FOR_FORGET
from app.config.config import (FROM_EMAIL, EMAIL_PASSWORD)
import string
import random
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from sendgrid import SendGridAPIClient
from app.auth.jwt_handler import generate_jwt_token
from sendgrid.helpers.mail import Mail
from fastapi import Request, status

from app.cores.managers.rbac.user import AuthenticationManager
from app.models.common.common import APIResponse, ErrorMessages, ResponseMessage, UnauthorizedResponse
from app.models.common.logger import Logger
from app.models.rbac.user_authentication import ForgotPasswordPayload, Register, UserInLogin, UserOutLogin, UserRegisterPayload, UserRegisterResponsePayload, VerifyEmailPayload


user_router = InferringRouter()


@cbv(user_router)
class UserController():
    def __init__(self):
        self.authentication_manager = AuthenticationManager()
        self.logger = Logger()

    
    @user_router.post("/login", summary="Login API", description="Returns the token of logged-in user",
             responses={status.HTTP_200_OK: {"model": UserOutLogin},
                        status.HTTP_401_UNAUTHORIZED: {"model": APIResponse},
                        status.HTTP_400_BAD_REQUEST: {"model": APIResponse},
                        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": APIResponse}})
    async def login(self, user: UserInLogin, request: Request) -> APIResponse or UnauthorizedResponse:
        try:

            if request.headers.get('cf-connecting-ip') is not None:
                user_ip = request.headers.get('cf-connecting-ip')
            elif request.client.host is not None:
                user_ip = request.client.host
            else:
                user_ip = IP

            user_ip = user_ip
            user_param = user.dict()
            user_param.update({
                "ip": user_ip
            })
            response = await self.authentication_manager.login(user_param)
            if isinstance(response, ResponseMessage):
                return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                                    content={"status": False, "message": "Login attempt fail. Invalid email or password"})
            if response.get("accessToken"):
                response.update({
                    "user": response["user"],
                    "token": generate_jwt_token({"user": response["user"],
                                                "access_token": response.get("accessToken"),
                                                "user_id": response.get("userId"),
                                                "user_email": response.get("email"),
                                                "user_role": response.get("userRole")})

                })
                return_data = UserOutLogin(**response, status=True, message="You are logged in successfully'")
                return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(return_data))
            return JSONResponse(status_code=response.status_code, content=response)
        except Exception as e:
            print(e)
            error = {
                "status": False,
                "message": ErrorMessages.server_busy_error.value
            }
            return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                content=error)


    @user_router.post("/register", response_model=Register, summary = "User Registration API", description = "Register a user with the system",
                responses={status.HTTP_200_OK: {"model": UserRegisterResponsePayload},
                            status.HTTP_401_UNAUTHORIZED: {"model": APIResponse},
                            status.HTTP_400_BAD_REQUEST: {"model": APIResponse},
                            status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": APIResponse}})
    async def register(self, requestPayload: Register) -> APIResponse or UnauthorizedResponse:

        try:
            characters = string.ascii_letters + string.digits
            random_key = ''.join(random.choice(characters) for _ in range(35))
            requestPayload_data = UserRegisterPayload(
                **requestPayload.dict(),  # Unpack requestPayload as a dictionary
                random_key=random_key,
                source="direct"
            )
            # requestPayload_data = UserRegisterPayload(dict(requestPayload), random_key=random_key, source="direct")
            response = await self.authentication_manager.register(requestPayload_data)
            if "message" in response:
                return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                                    content={"success": False, "message": "Email already exist."})
            tuple_as_string = ''.join(map(str, AUTH_LINK))
            result = tuple_as_string + random_key
            subject_link = result
            message = Mail(
                    from_email=FROM_EMAIL,
                    to_emails=requestPayload.email,
                    subject= "Websential.ca",
                    html_content=f'''<!DOCTYPE html>
                                    <html>
                                    <head>
                                        <title>My HTML Page</title>
                                    </head>
                                    <body>
                                    <div style="background: #eaedf1; display:flex; justify-content: center;">
                                            <div style="width: 50%;">
                                            <div style="background: #fff; padding: 10px; margin-top: 10px; margin-bottom: 10px;">
                                            <p>Dear Customer,</p>
                                            <p>To proceed please click on the button to verify your account.</p>

                                            <div style="display:flex; justify-content:center;">
                                            <a href="{subject_link}">
                                            <button style="padding:5px; background-color: #0a66c2; color: #fff; border-radius: 5px; border: 5px solid #0a66c2; cursor: pointer;">Verify Account</button>
                                            </a>
                                            </div>
                                            <p>Thank you for choosing SimplePay. We value your business.</p>
                                            <p>Please refer to following guide to get started: https://v3.simplepay.com/guides/#/general-guide</p>
                                            </div>
                                            <address style="line-height:0.375rem; font-size: 0.875rem; font-style: normal; padding-bottom: 20px;">
                                                <b>Hatchbox Inc.</b>
                                                <p>1550 South Gateway Rd., Suite 229</p>
                                                <p>Mississauga</p>
                                                <p>ON L4W5G6</p>
                                                <p>(905) 624-9559</p>
                                            </address>
                                            </div>
                                            </div>
                                    </body>
                                    </html>
                    '''
                )
            try:
                sg = SendGridAPIClient(EMAIL_PASSWORD)
                sg.send(message)
            except Exception as e:
                print(e)
                error = {
                "status": False,
                "message": ErrorMessages.server_busy_error.value
            }
                return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                    content=error)

            return JSONResponse(status_code=status.HTTP_201_CREATED, content={"success": True, "message": "User register successfully."})
        except Exception as e:
            print(e)
            error = {
                "status": False,
                "message": ErrorMessages.server_busy_error.value
            }
            return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                    content=error)
        

    @user_router.post("/send-email", summary = "Send email to user API", description = "Send email to user API",
             responses={status.HTTP_200_OK: {"model": APIResponse},
                        status.HTTP_401_UNAUTHORIZED: {"model": APIResponse},
                        status.HTTP_400_BAD_REQUEST: {"model": APIResponse},
                        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": APIResponse}})
    async def send_email(self, email: str) -> APIResponse or UnauthorizedResponse:
        try:
            characters = string.ascii_letters + string.digits
            random_key = ''.join(random.choice(characters) for _ in range(35))
            email_key_payload = {
                'email': email,
                'random_key':random_key
            }
            api_response = await self.authentication_manager.updated_with_email(email_key_payload)
            if "message" in api_response:
                return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                                    content={"success": False, "message": "User email not exist."})
            tuple_as_string = ''.join(map(str, LINK_FOR_FORGET))
            result = tuple_as_string + random_key
            subject_link = result
            message = Mail(
                    from_email=FROM_EMAIL,
                    to_emails=email,
                    subject= "Websential.ca",
                    html_content=f'''<!DOCTYPE html>
                                    <html>
                                    <head>
                                        <title>My HTML Page</title>
                                    </head>
                                    <body>
                                        <div style="background: #eaedf1; display: flex; justify-content: center !important;">
                                        <div style="width: 50%;">
                                        <div style="background: #fff; padding: 10px; margin-top: 10px; margin-bottom: 10px;">
                                        <p>Dear Customer,</p>
                                        <p>To Reset Password click on the button</p>

                                        <div style="display: flex; justify-content:center;">
                                        <a href="{subject_link}">
                                        <button style="padding: 5px; background-color: #0a66c2; color: #fff; border-radius: 5px; border: 5px solid #0a66c2; cursor: pointer !important;">Reset Password</button>
                                        </a>
                                        </div>
                                        </div>
                                        <address style="line-height: 0.375rem; font-size: 0.875rem; font-style: normal; padding-bottom: 20px;">
                                            <b>Hatchbox Inc.</b>
                                            <p>1550 South Gateway Rd., Suite 229</p>
                                            <p>Mississauga</p>
                                            <p>ON L4W5G6</p>
                                            <p>(905) 624-9559</p>
                                        </address>
                                        </div>
                                        </div>
                                                                    </body>
                                                                    </html>
                                                    '''
                )
            try:
                sg = SendGridAPIClient(EMAIL_PASSWORD)
                mail_response = sg.send(message)
                print(mail_response.status_code)
            except Exception as e:
                print(e)
                error = {
                "status": False,
                "message": ErrorMessages.server_busy_error.value
            }
                return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                    content=error)

            return JSONResponse(status_code=status.HTTP_200_OK, content={
                "status": True,
                "message": "Email send successfully"
            })
        except Exception as e:
            print(e)
            error = {
                "status": False,
                "message": ErrorMessages.server_busy_error.value
            }
            return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                    content=error)
        


    @user_router.get("/user_detail/{email_key}", summary="Get user detail by email key", description="Return user detail by email key",
                responses={status.HTTP_200_OK: {"model": APIResponse},
                        status.HTTP_401_UNAUTHORIZED: {"model": UnauthorizedResponse},
                        status.HTTP_400_BAD_REQUEST: {"model": APIResponse},
                        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": APIResponse}})
    async def email_key(self, email_key:str) -> APIResponse or UnauthorizedResponse:
        try:
            api_response = await self.authentication_manager.get_email_link_key(email_key)
            if not api_response:
                return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content="Invalid email key")
            api_response_data = Register(**api_response)

            return JSONResponse(status_code=status.HTTP_200_OK,
                        content={
                    'name': f"{api_response_data.first_name} {api_response_data.last_name}",
                    'email': api_response_data.email
                })
        # except ConnectionException:
        #     con_error_resp = {
        #         "status": False,
        #         "message": ErrorMessages.rbac_connection_error.value
        #     }
        #     return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        #                         content=con_error_resp)
        except Exception as e:
            print(e)
            error = {
                "status": False,
                "message": ErrorMessages.server_busy_error.value
            }
            return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                content=error)
        

    @user_router.post("/verify-email", summary = "Verify Email API", description = "API used to verify the email",
             responses={status.HTTP_200_OK: {"model": APIResponse},
                        status.HTTP_401_UNAUTHORIZED: {"model": UnauthorizedResponse},
                        status.HTTP_400_BAD_REQUEST: {"model": APIResponse},
                        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": APIResponse}})
    async def verify_email(self, requestPayload: VerifyEmailPayload) -> APIResponse or UnauthorizedResponse:
        try:
            api_response = await self.authentication_manager.verify_email(requestPayload)
            if not api_response:
                return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content="Invalid email")
            api_response_data = Register(**api_response)

            return JSONResponse(status_code=status.HTTP_200_OK,
                        content={
                    'name': f"{api_response_data.first_name} {api_response_data.last_name}",
                    'email': api_response_data.email
                })
        except Exception as e:
            print(e)
            con_error = {
                "status": False,
                "message": ErrorMessages.server_busy_error.value
            }
            return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                content=con_error)
        

    
    @user_router.post("/forgot-password", summary = "forgot Password API", description = "API used for reset the new password",
             responses={status.HTTP_200_OK: {"model": APIResponse},
                        status.HTTP_401_UNAUTHORIZED: {"model": UnauthorizedResponse},
                         status.HTTP_400_BAD_REQUEST: {"model": APIResponse},
                         status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": APIResponse}})
    async def forgot_password(self, requestPayload: ForgotPasswordPayload) -> APIResponse or UnauthorizedResponse:

        try:
            if requestPayload.new_password != requestPayload.confirm_new_password:
                return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content = {"success": False, "message": "New Password and confirm_new_password not matched"})
            api_response = await self.authentication_manager.set_password(requestPayload)
            if not api_response:
                return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content="Invalid email key")
            # return JSONResponse(status_code=status.HTTP_200_OK ,content="Password has been updated.")
            return JSONResponse(status_code=status.HTTP_200_OK, content = {"success": True, "message": "Password has been updated."})

        except Exception as e:
            print(e)
            error = {
                "status": False,
                "message": ErrorMessages.server_busy_error.value
            }
            return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                content=error)