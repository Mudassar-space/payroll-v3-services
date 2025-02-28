from fastapi import Depends, Query, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from app.auth.jwt_authentication import JWTAuthentication
from app.cores.managers.rbac.roles import RolesManager
from app.models.common.common import ErrorMessages, ResponseMessage
from app.models.common.logger import Logger
from app.models.rbac.data_roles import UserRolesListResponse, UserRolesRequestModel, UserRolesResponseModel

roles_router = InferringRouter()


@cbv(roles_router)
class RolesController():
    def __init__(self):
        self.roles_manager = RolesManager()
        self.logger = Logger()

    @roles_router.post("/",
                          summary="Create a role",
                          description="Create a role and return role with details",
                          status_code=status.HTTP_201_CREATED,
                          response_model=UserRolesRequestModel,
                          responses={status.HTTP_400_BAD_REQUEST: {"model": ResponseMessage},
                                     status.HTTP_401_UNAUTHORIZED: {"model": ResponseMessage},
                                     status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ResponseMessage},
                                     status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ResponseMessage}})
    async def create_role(self, payload: UserRolesRequestModel, token_data=Depends(JWTAuthentication())):
        try:
            response = await self.roles_manager.create_role(payload)
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
        

    @roles_router.get("/{id}/",
                summary="Get role by id",
                description="Returns role detail",
                responses={status.HTTP_200_OK: {"model": UserRolesResponseModel},
                           status.HTTP_401_UNAUTHORIZED: {"model": ResponseMessage},
                           status.HTTP_404_NOT_FOUND: {"model": ResponseMessage},
                           status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ResponseMessage},
                           status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ResponseMessage}})
    async def get_by_id(self, id: str, token_data=Depends(JWTAuthentication())):
        try:
            response = await self.roles_manager.get_by_id(id)
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

    @roles_router.delete("/{id}/",
                   summary="Delete role by id",
                   description="Returns confirmation if role is deleted or not",
                   responses={status.HTTP_200_OK: {"model": ResponseMessage},
                              status.HTTP_401_UNAUTHORIZED: {"model": ResponseMessage},
                              status.HTTP_403_FORBIDDEN: {"model": ResponseMessage},
                              status.HTTP_404_NOT_FOUND: {"model": ResponseMessage},
                              status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ResponseMessage},
                              status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ResponseMessage}})
    async def delete_by_id(self, id: str, token_data=Depends(JWTAuthentication())):
        try:
            response = await self.roles_manager.delete_by_id(id)
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

    @roles_router.put("/{id}/",
                summary="Update role by id",
                description="Update the branch by id and return the updated record",
                responses={status.HTTP_200_OK: {"model": UserRolesResponseModel},
                           status.HTTP_400_BAD_REQUEST: {"model": ResponseMessage},
                           status.HTTP_401_UNAUTHORIZED: {"model": ResponseMessage},
                           status.HTTP_403_FORBIDDEN: {"model": ResponseMessage},
                           status.HTTP_404_NOT_FOUND: {"model": ResponseMessage},
                           status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ResponseMessage},
                           status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ResponseMessage}})
    async def update_by_id(self, id: str, payload: UserRolesRequestModel, token_data=Depends(JWTAuthentication())):
        try:
            response = await self.roles_manager.update_by_id(id, payload)
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


    @roles_router.get("/",
                summary="Get roles List",
                description="Returns a List containing roles Objects",
                responses={status.HTTP_200_OK: {"model": UserRolesListResponse},
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

            response = await self.roles_manager.get_list(params)
            return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(response))
        except Exception as e:
            self.logger.error(e)
            message = ResponseMessage(
                success=False, message=ErrorMessages.SERVER_ERROR.value)
            response = JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=jsonable_encoder(message))
            return response