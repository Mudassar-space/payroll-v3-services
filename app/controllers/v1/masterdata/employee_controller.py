
from typing import List
from fastapi import Depends, Query, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from app.auth.jwt_authentication import JWTAuthentication
from app.cores.managers.master_data.employee_manager import EmployeeManager
from app.models.common.common import APIResponse, ErrorMessages, ResponseMessage, UnauthorizedResponse
from app.models.common.ddl_entity import DDLEntity
from app.models.common.logger import Logger
# from requests_async.exceptions import ConnectionError as ConnectionException
from app.models.master_data.employee_model import EmployeeListResponseModel, EmployeeResponse, EmployeeReuestPayload


employee_router = InferringRouter()


@cbv(employee_router)
class ClientController():
    def __init__(self):
        self.employee_manager = EmployeeManager()
        self.logger = Logger()



    @employee_router.post("/", status_code=status.HTTP_201_CREATED, response_model=EmployeeResponse,
                responses={status.HTTP_201_CREATED: {"model": EmployeeResponse},
                            status.HTTP_401_UNAUTHORIZED: {"model": UnauthorizedResponse},
                            status.HTTP_400_BAD_REQUEST: {"model": APIResponse},
                            status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": APIResponse}},
                summary="Create Employee",
                description="Returns created Employee")
    async def add_employee(self, payload: EmployeeReuestPayload, token_data=Depends(JWTAuthentication())):
        try:
            partner_token_data_dict = dict(token_data)
            created_by_external_id = partner_token_data_dict.get("user_id")
            created_by_email = partner_token_data_dict.get("user_email")
            employee_payload = EmployeeResponse(**dict(payload),
                                        created_by_external_id=created_by_external_id,
                                        created_by_email=created_by_email,
                                        )
            
            created_employee = await self.employee_manager.add_employee(employee_payload)
            if isinstance(created_employee, ResponseMessage):
                return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                                    content=jsonable_encoder(created_employee))

            if not isinstance(created_employee, ResponseMessage):
                return JSONResponse(status_code=status.HTTP_201_CREATED, content=jsonable_encoder(created_employee))

            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=jsonable_encoder(created_employee))
        # except ConnectionException:
        #     con_error = {
        #         "status": False,
        #         "message": "Master Data API connection not established."
        #     }
        #     return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=con_error)

        except Exception as e:
            self.logger.error(e)
            # print(e)
            message = ResponseMessage(
                success=False, message=ErrorMessages.server_error.value)
            response = JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=jsonable_encoder(message))
            return response


    @employee_router.delete("/{id}/",
                status_code=status.HTTP_204_NO_CONTENT,
                responses={status.HTTP_401_UNAUTHORIZED: {"model": UnauthorizedResponse},
                            status.HTTP_403_FORBIDDEN: {"model": APIResponse},
                            status.HTTP_404_NOT_FOUND: {"model": APIResponse},
                            status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": APIResponse}},
                summary="Delete Employee by id",
                description="Delete Employee by id")
    async def delete_employee_by_id(self, id:str, client_id: str, token_data=Depends(JWTAuthentication())):
        try:
            delete_response = await self.employee_manager.delete_by_id(id, client_id)
            if delete_response.success:
                return JSONResponse(status_code=status.HTTP_200_OK,content = jsonable_encoder(delete_response))
            if delete_response.success == False:    
                return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                                    content=jsonable_encoder(delete_response))
        # except ConnectionException:
        #     con_error = {
        #         "status": False,
        #         "message": "Master Data API connection not established."
        #     }
        #     return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=con_error)
        except Exception as e:
            self.logger.error(e)
            message = ResponseMessage(
                success=False, message=ErrorMessages.server_busy_error.value)
            response = JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=jsonable_encoder(message))
            return response
        
        
    @employee_router.get("/{id}/",
                summary="Get Employee details API",
                description="Return Employee details by ID",
                responses={status.HTTP_200_OK: {"model": EmployeeResponse},
                        status.HTTP_400_BAD_REQUEST: {"model": APIResponse},
                        status.HTTP_401_UNAUTHORIZED: {"model": UnauthorizedResponse},
                        status.HTTP_403_FORBIDDEN: {"model": APIResponse},
                        status.HTTP_404_NOT_FOUND: {"model": APIResponse},
                        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": APIResponse}})
    async def get_employee_detail(self, id:str, token_data=Depends(JWTAuthentication())):
        try:

            detail_response = await self.employee_manager.get_employee_details(id)
            if isinstance(detail_response, EmployeeResponse):
                return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(detail_response))
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=jsonable_encoder(detail_response))
        # except ConnectionException:
        #     con_error = {
        #         "status": False,
        #         "message": "Master Data API connection not established."
        #     }
        #     return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=con_error)
        except Exception as e:
            self.logger.error(e)
            # print(e)
            con_error = {
                "status": False,
                "message": e
            }

            return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=con_error)
        
        
        
    @employee_router.get("/",
                summary="Get list of Employee",
                description="Returns a list of Employee",
                responses={status.HTTP_200_OK: {"model": EmployeeListResponseModel},
                           status.HTTP_401_UNAUTHORIZED: {"model": ResponseMessage},
                           status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ResponseMessage},
                           status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ResponseMessage}})
    async def get_list(self, client_id:str, search_query: str = "", order_by: str = "name",
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
            response = await self.employee_manager.get_list(client_id, params)
            return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(response))

        except Exception as e:
            self.logger.error(e)
            # print(e)
            message = ResponseMessage(
                success=False, message=ErrorMessages.server_error.value)
            response = JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=jsonable_encoder(message))
            return response
        


    @employee_router.put("/{id}/",
                summary="Update Employee by id",
                description="Update the Employee & return the updated record",
                responses={status.HTTP_200_OK: {"model": EmployeeResponse},
                           status.HTTP_400_BAD_REQUEST: {"model": ResponseMessage},
                           status.HTTP_401_UNAUTHORIZED: {"model": ResponseMessage},
                           status.HTTP_403_FORBIDDEN: {"model": ResponseMessage},
                           status.HTTP_404_NOT_FOUND: {"model": ResponseMessage},
                           status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ResponseMessage},
                           status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ResponseMessage}})
    async def update_by_id(self, id: str, payload: EmployeeReuestPayload, partner_token_data=Depends(JWTAuthentication())) -> ResponseMessage:
        try:
            partner_token_data_dict = dict(partner_token_data)
            updated_by_external_id = partner_token_data_dict.get("user_id")
            updated_by_email = partner_token_data_dict.get("user_email")
            employee_payload = EmployeeResponse(**dict(payload),
                                        updated_by_external_id=updated_by_external_id,
                                        updated_by_email=updated_by_email,
                                        )
            response = await self.employee_manager.update_by_id(id, employee_payload)
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
        

    @employee_router.get("/field_value/{employee_id}/",
                summary="Get employee log details API",
                description="Return employee log details by ID",
                responses={status.HTTP_400_BAD_REQUEST: {"model": APIResponse},
                        status.HTTP_401_UNAUTHORIZED: {"model": UnauthorizedResponse},
                        status.HTTP_403_FORBIDDEN: {"model": APIResponse},
                        status.HTTP_404_NOT_FOUND: {"model": APIResponse},
                        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": APIResponse}})
    async def get_field_detail(self, employee_id: str, field_name: str, token_data=Depends(JWTAuthentication())):
        try:

            detail_response = await self.employee_manager.get_field_detail(employee_id, field_name)
            if type(detail_response) is list:
                return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(detail_response))
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=jsonable_encoder(detail_response))
        # except ConnectionException:
        #     con_error = {
        #         "status": False,
        #         "message": "Master Data API connection not established."
        #     }
        #     return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=con_error)
        except Exception as e:
            self.logger.error(e)
            # print(e)
            # print(e)
            con_error = {
                "status": False,
                "message": e
            }

            return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=con_error)
        

    @employee_router.get("/ddl",
                response_model=List[DDLEntity],
                summary="Get  ddl List",
                description="Returns a dll List containing  Objects",
                responses={
                           status.HTTP_401_UNAUTHORIZED: {"model": ResponseMessage},
                           status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ResponseMessage},
                           status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ResponseMessage}})
    async def get_dll_list(self, client_id: str,  token_data=Depends(JWTAuthentication())):
        try:
            response = await self.employee_manager.get_ddl_list(client_id)
            return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(response))
        except Exception as e:
            self.logger.error(e)
            print(e)
            message = ResponseMessage(
                success=False, message=ErrorMessages.server_error.value)
            response = JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=jsonable_encoder(message))
            return response