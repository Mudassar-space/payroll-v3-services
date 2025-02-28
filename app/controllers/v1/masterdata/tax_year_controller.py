from typing import List
from fastapi import Depends, Query, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from app.auth.jwt_authentication import JWTAuthentication
from app.cores.managers.master_data.tax_year_manager import TaxYearManager
from app.models.common.ddl_entity import DDLEntity
from app.models.master_data.departments import DepartmentListResponseModel, DepartmentRequestPayload, DepartmentResponsePayload
from app.models.common.common import ErrorMessages, ResponseMessage
from app.models.common.logger import Logger
from app.models.master_data.designation import DesignationListResponseModel, DesignationRequestPayload, DesignationResponsePayload
from app.models.master_data.tax_year import TaxYearListResponseModel, TaxYearRequestPayload, TaxYearResponsePayload

tax_year_router = InferringRouter()


@cbv(tax_year_router)
class TaxYearController():
    def __init__(self):
        self.tax_year_manager = TaxYearManager()
        self.logger = Logger()

    @tax_year_router.post("/",
                          summary="Create a Tax Year",
                          description="Create a Tax Year and return Tax Year with details",
                          status_code=status.HTTP_201_CREATED,
                          response_model=TaxYearRequestPayload,
                          responses={status.HTTP_400_BAD_REQUEST: {"model": ResponseMessage},
                                     status.HTTP_401_UNAUTHORIZED: {"model": ResponseMessage},
                                     status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ResponseMessage},
                                     status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ResponseMessage}})
    async def create(self, payload: TaxYearRequestPayload, token_data=Depends(JWTAuthentication())):
        try:
            partner_token_data_dict = dict(token_data)
            created_by_external_id = partner_token_data_dict.get("user_id")
            created_by_email = partner_token_data_dict.get("user_email")
            tax_year_payload = TaxYearResponsePayload(**dict(payload),
                                        created_by_external_id=created_by_external_id,
                                        created_by_email=created_by_email,
                                        )
            response = await self.tax_year_manager.create(tax_year_payload)
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
        

    @tax_year_router.get("/{id}/",
                summary="Get Tax Year by id",
                description="Returns Tax Year detail",
                responses={status.HTTP_200_OK: {"model": TaxYearResponsePayload},
                           status.HTTP_401_UNAUTHORIZED: {"model": ResponseMessage},
                           status.HTTP_404_NOT_FOUND: {"model": ResponseMessage},
                           status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ResponseMessage},
                           status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ResponseMessage}})
    async def get_by_id(self, id: str, token_data=Depends(JWTAuthentication())):
        try:
            response = await self.tax_year_manager.get_by_id(id)
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

    @tax_year_router.delete("/{id}/",
                   summary="Delete Tax Year by id",
                   description="Returns confirmation if Tax Year is deleted or not",
                   responses={status.HTTP_200_OK: {"model": ResponseMessage},
                              status.HTTP_401_UNAUTHORIZED: {"model": ResponseMessage},
                              status.HTTP_403_FORBIDDEN: {"model": ResponseMessage},
                              status.HTTP_404_NOT_FOUND: {"model": ResponseMessage},
                              status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ResponseMessage},
                              status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ResponseMessage}})
    async def delete_by_id(self, id: str, token_data=Depends(JWTAuthentication())):
        try:
            response = await self.tax_year_manager.delete_by_id(id)
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

    @tax_year_router.put("/{id}/",
                summary="Update Tax Year by id",
                description="Update the Tax Year by id and return the updated record",
                responses={status.HTTP_200_OK: {"model": TaxYearResponsePayload},
                           status.HTTP_400_BAD_REQUEST: {"model": ResponseMessage},
                           status.HTTP_401_UNAUTHORIZED: {"model": ResponseMessage},
                           status.HTTP_403_FORBIDDEN: {"model": ResponseMessage},
                           status.HTTP_404_NOT_FOUND: {"model": ResponseMessage},
                           status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ResponseMessage},
                           status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ResponseMessage}})
    async def update_by_id(self, id: str, payload: TaxYearRequestPayload, token_data=Depends(JWTAuthentication())):
        try:
            partner_token_data_dict = dict(token_data)
            updated_by_external_id = partner_token_data_dict.get("user_id")
            updated_by_email = partner_token_data_dict.get("user_email")
            tax_year_payload = TaxYearResponsePayload(**dict(payload),
                                        updated_by_external_id=updated_by_external_id,
                                        updated_by_email=updated_by_email,
                                        )
            response = await self.tax_year_manager.update_by_id(id, tax_year_payload)
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

    @tax_year_router.get("/",
                summary="Get Tax Year List",
                description="Returns a List containing Tax Year Objects",
                responses={status.HTTP_200_OK: {"model": TaxYearListResponseModel},
                           status.HTTP_401_UNAUTHORIZED: {"model": ResponseMessage},
                           status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ResponseMessage},
                           status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ResponseMessage}})
    async def get_list(self, search_query: str = "", order_by: str = "name",
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

            response = await self.tax_year_manager.get_list(params)
            return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(response))
        except Exception as e:
            # self.logger.error(e)
            print(e)
            message = ResponseMessage(
                success=False, message=ErrorMessages.server_error.value)
            response = JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=jsonable_encoder(message))
            return response
        


    @tax_year_router.get("/tax-year-ddl",
                response_model=List[DDLEntity],
                summary="Get Tax Year ddl List",
                description="Returns a dll List containing Tax Year Objects",
                responses={
                           status.HTTP_401_UNAUTHORIZED: {"model": ResponseMessage},
                           status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ResponseMessage},
                           status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ResponseMessage}})
    async def get_dll_list(self, token_data=Depends(JWTAuthentication())):
        try:
            response = await self.tax_year_manager.get_ddl_list()
            return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(response))
        except Exception as e:
            self.logger.error(e)
            print(e)
            message = ResponseMessage(
                success=False, message=ErrorMessages.server_error.value)
            response = JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=jsonable_encoder(message))
            return response
        