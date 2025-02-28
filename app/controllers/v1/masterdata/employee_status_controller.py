from typing import List
from fastapi import Depends, Query, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from app.auth.jwt_authentication import JWTAuthentication
from app.cores.managers.master_data.emloyee_status_manager import EmployeeStatusManager
from app.models.common.ddl_entity import DDLEntity
from app.models.common.common import ErrorMessages, ResponseMessage
from app.models.common.logger import Logger
from app.models.master_data.employee_status import EmployeeStatusListResponseModel, EmployeeStatusResponsePayload, EmployeeStatusRequestPayload

employee_status_router = InferringRouter()


@cbv(employee_status_router)
class EmployeeStatusController():
    def __init__(self):
        self.employee_status_manager = EmployeeStatusManager()
        self.logger = Logger()

    @employee_status_router.post("/",
                          summary="Create a Employee status",
                          description="Create a Employee status and return Employee status with details",
                          status_code=status.HTTP_201_CREATED,
                          response_model=EmployeeStatusRequestPayload,
                          responses={status.HTTP_400_BAD_REQUEST: {"model": ResponseMessage},
                                     status.HTTP_401_UNAUTHORIZED: {"model": ResponseMessage},
                                     status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ResponseMessage},
                                     status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ResponseMessage}})
    async def create(self,client_id:str, payload: EmployeeStatusRequestPayload, token_data=Depends(JWTAuthentication())):
        try:
            partner_token_data_dict = dict(token_data)
            created_by_external_id = partner_token_data_dict.get("user_id")
            created_by_email = partner_token_data_dict.get("user_email")
            request_payload_data = EmployeeStatusResponsePayload(**dict(payload),
                                        client_id=client_id,
                                        created_by_external_id=created_by_external_id,
                                        created_by_email=created_by_email,
                                        )
            response = await self.employee_status_manager.create(request_payload_data)
            if not isinstance(response, ResponseMessage):
                return JSONResponse(status_code=status.HTTP_201_CREATED, content=jsonable_encoder(response))
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=jsonable_encoder(response))
        except Exception as e:
            self.logger.error(e)
            print(e)
            message = ResponseMessage(
                success=False, message=ErrorMessages.server_error.value)
            response = JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=jsonable_encoder(message))
            return response
        

    @employee_status_router.get("/{id}/",
                summary="Get employee status by id",
                description="Returns employee status detail",
                responses={status.HTTP_200_OK: {"model": EmployeeStatusResponsePayload},
                           status.HTTP_401_UNAUTHORIZED: {"model": ResponseMessage},
                           status.HTTP_404_NOT_FOUND: {"model": ResponseMessage},
                           status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ResponseMessage},
                           status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ResponseMessage}})
    async def get_by_id(self,client_id:str, id: str, token_data=Depends(JWTAuthentication())):
        try:
            response = await self.employee_status_manager.get_by_id(client_id, id)
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

    @employee_status_router.delete("/{id}/",
                   summary="Delete employee status by id",
                   description="Returns confirmation if employee status is deleted or not",
                   responses={status.HTTP_200_OK: {"model": ResponseMessage},
                              status.HTTP_401_UNAUTHORIZED: {"model": ResponseMessage},
                              status.HTTP_403_FORBIDDEN: {"model": ResponseMessage},
                              status.HTTP_404_NOT_FOUND: {"model": ResponseMessage},
                              status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ResponseMessage},
                              status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ResponseMessage}})
    async def delete_by_id(self, id: str, token_data=Depends(JWTAuthentication())):
        try:
            response = await self.employee_status_manager.delete_by_id(id)
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

    @employee_status_router.put("/{id}/",
                summary="Update employee status by id",
                description="Update the employee status by id and return the updated record",
                responses={status.HTTP_200_OK: {"model": EmployeeStatusResponsePayload},
                           status.HTTP_400_BAD_REQUEST: {"model": ResponseMessage},
                           status.HTTP_401_UNAUTHORIZED: {"model": ResponseMessage},
                           status.HTTP_403_FORBIDDEN: {"model": ResponseMessage},
                           status.HTTP_404_NOT_FOUND: {"model": ResponseMessage},
                           status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ResponseMessage},
                           status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ResponseMessage}})
    async def update_by_id(self, id: str, payload: EmployeeStatusRequestPayload, token_data=Depends(JWTAuthentication())):
        try:
            partner_token_data_dict = dict(token_data)
            updated_by_external_id = partner_token_data_dict.get("user_id")
            updated_by_email = partner_token_data_dict.get("user_email")
            request_payload_data = EmployeeStatusResponsePayload(**dict(payload),
                                        updated_by_external_id=updated_by_external_id,
                                        updated_by_email=updated_by_email,
                                        )
            response = await self.employee_status_manager.update_by_id(id, request_payload_data)
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

    @employee_status_router.get("/",
                summary="Get employee status List",
                description="Returns a List containing employee status Objects",
                responses={status.HTTP_200_OK: {"model": EmployeeStatusListResponseModel},
                           status.HTTP_401_UNAUTHORIZED: {"model": ResponseMessage},
                           status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ResponseMessage},
                           status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ResponseMessage}})
    async def get_list(self,client_id:str, search_query: str = "", order_by: str = "name",
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

            response = await self.employee_status_manager.get_list(client_id, params)
            return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(response))
        except Exception as e:
            self.logger.error(e)
            print(e)
            message = ResponseMessage(
                success=False, message=ErrorMessages.server_error.value)
            response = JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=jsonable_encoder(message))
            return response
        


    @employee_status_router.get("/employee-status-ddl",
                response_model=List[DDLEntity],
                summary="Get employee status ddl List",
                description="Returns a dll List containing employee status Objects",
                responses={
                           status.HTTP_401_UNAUTHORIZED: {"model": ResponseMessage},
                           status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ResponseMessage},
                           status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ResponseMessage}})
    async def get_dll_list(self,client_id:str, token_data=Depends(JWTAuthentication())):
        try:
            response = await self.employee_status_manager.get_ddl_list(client_id)
            return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(response))
        except Exception as e:
            self.logger.error(e)
            print(e)
            message = ResponseMessage(
                success=False, message=ErrorMessages.server_error.value)
            response = JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=jsonable_encoder(message))
            return response
        