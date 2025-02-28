
from typing import List
from fastapi import Depends, Query, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi_utils.cbv import cbv

from fastapi_utils.inferring_router import InferringRouter

from app.auth.jwt_authentication import JWTAuthentication
from app.cores.managers.master_data.client_bank_manager import ClientBankManager
from app.models.common.common import APIResponse, ErrorMessages, ResponseMessage, UnauthorizedResponse
from app.models.common.ddl_entity import DDLEntity
from app.models.common.logger import Logger


from requests_async.exceptions import ConnectionError as ConnectionException

from app.models.master_data.accountant_bank import AccountantBank, AccountantBankResponse
from app.models.master_data.client_bank_model import ClientBank, ClientBankResponse


client_bank_router = InferringRouter()


@cbv(client_bank_router)
class ClientBankController():
    def __init__(self):
        self.client_bank_manager = ClientBankManager()
        self.logger = Logger()



    @client_bank_router.post("/", status_code=status.HTTP_201_CREATED, response_model=ClientBankResponse,
                responses={status.HTTP_201_CREATED: {"model": ClientBankResponse},
                            status.HTTP_401_UNAUTHORIZED: {"model": UnauthorizedResponse},
                            status.HTTP_400_BAD_REQUEST: {"model": APIResponse},
                            status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": APIResponse}},
                summary="Create Client Bank",
                description="Returns created client bank")
    async def add_bank(self, payload: ClientBank, token_data=Depends(JWTAuthentication())):
        try:
            partner_token_data_dict = dict(token_data)
            created_by_external_id = partner_token_data_dict.get("user_id")
            created_by_email = partner_token_data_dict.get("user_email")
            bank_payload = ClientBankResponse(**dict(payload),
                                        created_by_external_id=created_by_external_id,
                                        created_by_email=created_by_email,
                                        )
            
            created_bank = await self.client_bank_manager.add_bank(bank_payload)
            if isinstance(created_bank, ResponseMessage):
                return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                                    content=jsonable_encoder(created_bank))

            if not isinstance(created_bank, ResponseMessage):
                return JSONResponse(status_code=status.HTTP_201_CREATED, content=jsonable_encoder(created_bank))

        except Exception as e:
            self.logger.error(e)
            # print(e)
            message = ResponseMessage(
                success=False, message=ErrorMessages.server_error.value)
            response = JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=jsonable_encoder(message))
            return response


    @client_bank_router.delete("/{bank_id}/",
                status_code=status.HTTP_204_NO_CONTENT,
                responses={status.HTTP_401_UNAUTHORIZED: {"model": UnauthorizedResponse},
                            status.HTTP_403_FORBIDDEN: {"model": APIResponse},
                            status.HTTP_404_NOT_FOUND: {"model": APIResponse},
                            status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": APIResponse}},
                summary="Delete Client bank by id",
                description="Delete Client bank by id")
    async def delete_bank_by_id(self, bank_id: str, token_data=Depends(JWTAuthentication())):
        try:
            delete_response = await self.client_bank_manager.delete_by_id(bank_id)
            if delete_response.success:
                return JSONResponse(status_code=status.HTTP_200_OK,content = jsonable_encoder(delete_response))
            if delete_response.success == False:    
                return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                                    content=jsonable_encoder(delete_response))
        except Exception as e:
            self.logger.error(e)
            message = ResponseMessage(
                success=False, message=ErrorMessages.server_busy_error.value)
            response = JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=jsonable_encoder(message))
            return response
        
        
    @client_bank_router.get("/{bank_id}/",
                summary="Get client bank details API",
                description="Return client bank details by ID",
                responses={status.HTTP_200_OK: {"model": ClientBankResponse},
                        status.HTTP_400_BAD_REQUEST: {"model": APIResponse},
                        status.HTTP_401_UNAUTHORIZED: {"model": UnauthorizedResponse},
                        status.HTTP_403_FORBIDDEN: {"model": APIResponse},
                        status.HTTP_404_NOT_FOUND: {"model": APIResponse},
                        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": APIResponse}})
    async def get_bank_detail(self, bank_id: str, token_data=Depends(JWTAuthentication())):
        try:

            detail_response = await self.client_bank_manager.get_bank_details(str(bank_id))
            if isinstance(detail_response,ClientBankResponse):
                return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(detail_response))
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=jsonable_encoder(detail_response))
        except Exception as e:
            self.logger.error(e)
            con_error = {
                "status": False,
                "message": e
            }

            return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=con_error)
        
        
        
    @client_bank_router.get("/",
                summary="Get list of Client Bank",
                description="Returns  a list of Client bank",
                responses={status.HTTP_401_UNAUTHORIZED: {"model": ResponseMessage},
                           status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ResponseMessage},
                           status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ResponseMessage}})
    async def get_list(self, client_id: str, search_query: str = "", order_by: str = "name",
                       order_direction: str = "asc",
                       page: int = Query(default=1, ge=1), size: int = Query(default=50, ge=1, le=100), partner_token_data=Depends(JWTAuthentication())) -> ResponseMessage:
        params = {
            "search_query": search_query,
            "order_by": order_by,
            "order_direction": order_direction,
            "page": page,
            "size": size,
        }

        try:
            response = await self.client_bank_manager.get_list(client_id, params)
            return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(response))

        except Exception as e:
            self.logger.error(e)
            # print(e)
            message = ResponseMessage(
                success=False, message=ErrorMessages.server_error.value)
            response = JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=jsonable_encoder(message))
            return response
        


    @client_bank_router.put("/{bank_id}/",
                summary="Update Bank details",
                description="Update bank details & return the updated record",
                responses={status.HTTP_200_OK: {"model": ClientBankResponse},
                           status.HTTP_400_BAD_REQUEST: {"model": ResponseMessage},
                           status.HTTP_401_UNAUTHORIZED: {"model": ResponseMessage},
                           status.HTTP_403_FORBIDDEN: {"model": ResponseMessage},
                           status.HTTP_404_NOT_FOUND: {"model": ResponseMessage},
                           status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ResponseMessage},
                           status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ResponseMessage}})
    async def update_by_id(self, bank_id: str, payload: ClientBank, partner_token_data=Depends(JWTAuthentication())) -> ResponseMessage:
        try:
            partner_token_data_dict = dict(partner_token_data)
            updated_by_external_id = partner_token_data_dict.get("user_id")
            updated_by_email = partner_token_data_dict.get("user_email")
            client_bank_payload = ClientBankResponse(**dict(payload),
                                        updated_by_external_id=updated_by_external_id,
                                        updated_by_email=updated_by_email,
                                        )
            response = await self.client_bank_manager.update_by_id(bank_id, client_bank_payload)
            if not isinstance(response, ResponseMessage):
                return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(response))
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=jsonable_encoder(response))

        except Exception as e:
            # self.logger.error(e)
            print(e)
            message = ResponseMessage(
                success=False, message=ErrorMessages.server_error.value)
            response = JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=jsonable_encoder(message))
            return response
        

    @client_bank_router.get("/ddl",
                response_model=List[DDLEntity],
                summary="Get  ddl List",
                description="Returns a dll List containing  Objects",
                responses={
                           status.HTTP_401_UNAUTHORIZED: {"model": ResponseMessage},
                           status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ResponseMessage},
                           status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ResponseMessage}})
    async def get_dll_list(self, client_id: str,  token_data=Depends(JWTAuthentication())):
        try:
            response = await self.client_bank_manager.get_ddl_list(client_id)
            return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(response))
        except Exception as e:
            self.logger.error(e)
            print(e)
            message = ResponseMessage(
                success=False, message=ErrorMessages.server_error.value)
            response = JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=jsonable_encoder(message))
            return response