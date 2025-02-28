from typing import List
from fastapi import Depends, Query, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from app.auth.jwt_authentication import JWTAuthentication
from app.cores.managers.master_data.reimbursement_manager import ReimbursementManager
from app.models.common.ddl_entity import DDLEntity
from app.models.common.common import ErrorMessages, ResponseMessage
from app.models.master_data.reimbursement import ReimbursementListResponseModel, ReimbursementRequestPayload, ReimbursementResponsePayload
from app.models.common.logger import Logger

reimbursement_router = InferringRouter()


@cbv(reimbursement_router)
class ReimbursementController():
    def __init__(self):
        self.reimbursement_manager = ReimbursementManager()
        self.logger = Logger()

    @reimbursement_router.post("/",
                          summary="Create a Reimbursement",
                          description="Create a Reimbursement and return Reimbursement with details",
                          status_code=status.HTTP_201_CREATED,
                          response_model=ReimbursementResponsePayload,
                          responses={status.HTTP_400_BAD_REQUEST: {"model": ResponseMessage},
                                     status.HTTP_401_UNAUTHORIZED: {"model": ResponseMessage},
                                     status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ResponseMessage},
                                     status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ResponseMessage}})
    async def create(self, payload: ReimbursementRequestPayload, token_data=Depends(JWTAuthentication())):
        try:
            partner_token_data_dict = dict(token_data)
            created_by_external_id = partner_token_data_dict.get("user_id")
            created_by_email = partner_token_data_dict.get("user_email")
            reimbursement_payload = ReimbursementResponsePayload(**dict(payload),
                                        created_by_external_id=created_by_external_id,
                                        created_by_email=created_by_email,
                                        )
            response = await self.reimbursement_manager.create(reimbursement_payload)
            if not isinstance(response, ResponseMessage):
                return JSONResponse(status_code=status.HTTP_201_CREATED, content=jsonable_encoder(response))
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=jsonable_encoder(response))
        except Exception as e:
            # self.logger.error(e)
            print(e)
            message = ResponseMessage(
                success=False, message=ErrorMessages.server_error.value)
            response = JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=jsonable_encoder(message))
            return response
        

    @reimbursement_router.get("/{id}/",
                summary="Get Reimbursement by id",
                description="Returns Reimbursement detail",
                responses={status.HTTP_200_OK: {"model": ReimbursementResponsePayload},
                           status.HTTP_401_UNAUTHORIZED: {"model": ResponseMessage},
                           status.HTTP_404_NOT_FOUND: {"model": ResponseMessage},
                           status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ResponseMessage},
                           status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ResponseMessage}})
    async def get_by_id(self, id: str, token_data=Depends(JWTAuthentication())):
        try:
            response = await self.reimbursement_manager.get_by_id(id)
            if not isinstance(response, ResponseMessage):
                return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(response))
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=jsonable_encoder(response))
        except Exception as e:
            self.logger.error(e)
            print(e)
            message = ResponseMessage(
                success=False, message=ErrorMessages.server_error.value)
            response = JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=jsonable_encoder(message))
            return response

    @reimbursement_router.delete("/{id}/",
                   summary="Delete Reimbursement by id",
                   description="Returns confirmation if Reimbursement is deleted or not",
                   responses={status.HTTP_200_OK: {"model": ResponseMessage},
                              status.HTTP_401_UNAUTHORIZED: {"model": ResponseMessage},
                              status.HTTP_403_FORBIDDEN: {"model": ResponseMessage},
                              status.HTTP_404_NOT_FOUND: {"model": ResponseMessage},
                              status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ResponseMessage},
                              status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ResponseMessage}})
    async def delete_by_id(self, id: str, token_data=Depends(JWTAuthentication())):
        try:
            response = await self.reimbursement_manager.delete_by_id(id)
            if response.success:
                return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content=jsonable_encoder(response))
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=jsonable_encoder(response))
        except Exception as e:
            self.logger.error(e)
            print(e)
            message = ResponseMessage(
                success=False, message=ErrorMessages.server_error.value)
            response = JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=jsonable_encoder(message))
            return response

    @reimbursement_router.put("/{id}/",
                summary="Update Reimbursement by id",
                description="Update the Reimbursement by id and return the updated record",
                responses={status.HTTP_200_OK: {"model": ReimbursementResponsePayload},
                           status.HTTP_400_BAD_REQUEST: {"model": ResponseMessage},
                           status.HTTP_401_UNAUTHORIZED: {"model": ResponseMessage},
                           status.HTTP_403_FORBIDDEN: {"model": ResponseMessage},
                           status.HTTP_404_NOT_FOUND: {"model": ResponseMessage},
                           status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ResponseMessage},
                           status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ResponseMessage}})
    async def update_by_id(self, id: str, payload: ReimbursementRequestPayload, token_data=Depends(JWTAuthentication())):
        try:
            partner_token_data_dict = dict(token_data)
            updated_by_external_id = partner_token_data_dict.get("user_id")
            updated_by_email = partner_token_data_dict.get("user_email")
            reimbursement_payload = ReimbursementResponsePayload(**dict(payload),
                                        updated_by_external_id=updated_by_external_id,
                                        updated_by_email=updated_by_email,
                                        )
            response = await self.reimbursement_manager.update_by_id(id, reimbursement_payload)
            if not isinstance(response, ResponseMessage):
                return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(response))
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=jsonable_encoder(response))
        except Exception as e:
            self.logger.error(e)
            print(e)
            message = ResponseMessage(
                success=False, message=ErrorMessages.server_error.value)
            response = JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=jsonable_encoder(message))
            return response

    @reimbursement_router.get("/",
                summary="Get Reimbursement List",
                description="Returns a List containing Reimbursement Objects",
                responses={status.HTTP_200_OK: {"model": ReimbursementListResponseModel},
                           status.HTTP_401_UNAUTHORIZED: {"model": ResponseMessage},
                           status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ResponseMessage},
                           status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ResponseMessage}})
    async def get_list(self, client_id:str, search_query: str = "", order_by: str = "name",
                       order_direction: str = "asc",
                       page: int = Query(default=1, ge=1), size: int = Query(default=50, ge=1, le=100), token_data=Depends(JWTAuthentication())):
        try:
            params = {
                "search_query": search_query,
                "order_by": order_by,
                "order_direction": order_direction,
                "page": page,
                "size": size,
            }

            response = await self.reimbursement_manager.get_list(client_id, params)
            return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(response))
        except Exception as e:
            self.logger.error(e)
            print(e)
            message = ResponseMessage(
                success=False, message=ErrorMessages.server_error.value)
            response = JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=jsonable_encoder(message))
            return response
        


    @reimbursement_router.get("/reimbursement-ddl",
                response_model=List[DDLEntity],
                summary="Get reimbursement ddl List",
                description="Returns a dll List containing reimbursement Objects",
                responses={
                           status.HTTP_401_UNAUTHORIZED: {"model": ResponseMessage},
                           status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ResponseMessage},
                           status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ResponseMessage}})
    async def get_dll_list(self,client_id:str,  token_data=Depends(JWTAuthentication())):
        try:
            response = await self.reimbursement_manager.get_ddl_list(client_id)
            return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(response))
        except Exception as e:
            self.logger.error(e)
            print(e)
            message = ResponseMessage(
                success=False, message=ErrorMessages.server_error.value)
            response = JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=jsonable_encoder(message))
            return response
        