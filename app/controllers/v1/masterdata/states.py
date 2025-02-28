from typing import List
from fastapi import Depends, Query, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from app.auth.jwt_authentication import JWTAuthentication
from app.cores.managers.master_data.states import StatesManager
from app.models.master_data.states import StatesDdlListResponse, StatesListResponse, StatesRequestPayload, StatesResponsePayload
from app.models.common.common import ErrorMessages, ResponseMessage
from app.models.common.logger import Logger

states_router = InferringRouter()


@cbv(states_router)
class StatesController():
    def __init__(self):
        self.states_manager = StatesManager()
        self.logger = Logger()

    @states_router.post("/",
                          summary="Create a States",
                          description="Create a States and return States with details",
                          status_code=status.HTTP_201_CREATED,
                          response_model=StatesRequestPayload,
                          responses={status.HTTP_400_BAD_REQUEST: {"model": ResponseMessage},
                                     status.HTTP_401_UNAUTHORIZED: {"model": ResponseMessage},
                                     status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ResponseMessage},
                                     status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ResponseMessage}})
    async def create(self, payload: StatesRequestPayload, token_data=Depends(JWTAuthentication())):
        try:
            response = await self.states_manager.create(payload)
            if not isinstance(response, ResponseMessage):
                return JSONResponse(status_code=status.HTTP_201_CREATED, content=jsonable_encoder(response))
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=jsonable_encoder(response))
        except Exception as e:
            self.logger.error(e)
            message = ResponseMessage(
                success=False, message=ErrorMessages.SERVER_ERROR.value)
            response = JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=jsonable_encoder(message))
            return response
        

    @states_router.get("/{id}/",
                summary="Get States by id",
                description="Returns States detail",
                responses={status.HTTP_200_OK: {"model": StatesResponsePayload},
                           status.HTTP_401_UNAUTHORIZED: {"model": ResponseMessage},
                           status.HTTP_404_NOT_FOUND: {"model": ResponseMessage},
                           status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ResponseMessage},
                           status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ResponseMessage}})
    async def get_by_id(self, id: str, token_data=Depends(JWTAuthentication())):
        try:
            response = await self.states_manager.get_by_id(id)
            if not isinstance(response, ResponseMessage):
                return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(response))
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=jsonable_encoder(response))
        except Exception as e:
            self.logger.error(e)
            message = ResponseMessage(
                success=False, message=ErrorMessages.SERVER_ERROR.value)
            response = JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=jsonable_encoder(message))
            return response

    @states_router.delete("/{id}/",
                   summary="Delete States by id",
                   description="Returns confirmation if States is deleted or not",
                   responses={status.HTTP_200_OK: {"model": ResponseMessage},
                              status.HTTP_401_UNAUTHORIZED: {"model": ResponseMessage},
                              status.HTTP_403_FORBIDDEN: {"model": ResponseMessage},
                              status.HTTP_404_NOT_FOUND: {"model": ResponseMessage},
                              status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ResponseMessage},
                              status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ResponseMessage}})
    async def delete_by_id(self, id: str, token_data=Depends(JWTAuthentication())):
        try:
            response = await self.states_manager.delete_by_id(id)
            if response.success:
                return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(response))
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=jsonable_encoder(response))
        except Exception as e:
            self.logger.error(e)
            message = ResponseMessage(
                success=False, message=ErrorMessages.SERVER_ERROR.value)
            response = JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=jsonable_encoder(message))
            return response

    @states_router.put("/{id}/",
                summary="Update States by id",
                description="Update the States by id and return the updated record",
                responses={status.HTTP_200_OK: {"model": StatesResponsePayload},
                           status.HTTP_400_BAD_REQUEST: {"model": ResponseMessage},
                           status.HTTP_401_UNAUTHORIZED: {"model": ResponseMessage},
                           status.HTTP_403_FORBIDDEN: {"model": ResponseMessage},
                           status.HTTP_404_NOT_FOUND: {"model": ResponseMessage},
                           status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ResponseMessage},
                           status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ResponseMessage}})
    async def update_by_id(self, id: str, payload: StatesRequestPayload, token_data=Depends(JWTAuthentication())):
        try:
            response = await self.states_manager.update_by_id(id, payload)
            if not isinstance(response, ResponseMessage):
                return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(response))
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=jsonable_encoder(response))
        except Exception as e:
            self.logger.error(e)
            message = ResponseMessage(
                success=False, message=ErrorMessages.SERVER_ERROR.value)
            response = JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=jsonable_encoder(message))
            return response

    @states_router.get("/",
                summary="Get States List",
                description="Returns a List containing States Objects",
                responses={status.HTTP_200_OK: {"model": StatesListResponse},
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

            response = await self.states_manager.get_list(params)
            return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(response))
        except Exception as e:
            self.logger.error(e)
            message = ResponseMessage(
                success=False, message=ErrorMessages.SERVER_ERROR.value)
            response = JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=jsonable_encoder(message))
            return response
        


    @states_router.get("/ddl",
                response_model=List[StatesDdlListResponse],
                summary="Get  ddl List",
                description="Returns a dll List containing  Objects",
                responses={
                           status.HTTP_401_UNAUTHORIZED: {"model": ResponseMessage},
                           status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ResponseMessage},
                           status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ResponseMessage}})
    async def get_dll_list(self, country_id: str, token_data=Depends(JWTAuthentication())):
        try:
            response = await self.states_manager.get_ddl_list(country_id)
            return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(response))
        except Exception as e:
            self.logger.error(e)
            print(e)
            message = ResponseMessage(
                success=False, message=ErrorMessages.server_error.value)
            response = JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=jsonable_encoder(message))
            return response