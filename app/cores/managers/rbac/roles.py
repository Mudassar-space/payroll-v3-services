from app.database.rbac.roles import RolesDatabase
from app.models.common.common import  ResponseMessage
from bson.errors import InvalidId
from app.models.common.data_grid_header_column import DataGridHeaderColumn
from app.models.common.logger import Logger
from app.models.common.py_object_id import PyObjectId
from app.models.rbac.data_roles import UserRolesListResponse, UserRolesResponseModel



class RolesManager():
    def __init__(self) -> None:
        self.roles_database = RolesDatabase()
        self.logger = Logger()


    async def create_role(self, payload: UserRolesResponseModel):
        where_clouse = {"roleName": payload.role_name}
        already_exist = await self.roles_database.get_by_whereclouse(where_clouse)
        if already_exist:
            return ResponseMessage(success=False, message="Record already Exist with Role Name.")
        response = await self.roles_database.create_role(payload)
        return response
    
    async def get_by_id(self, id: str):
        response = self.validate_id(id)
        if isinstance(response, ResponseMessage):
            return response
        object_id = response
        where_clouse = {"_id": object_id}
        response = await self.roles_database.get_by_whereclouse(where_clouse)
        if response:
            response["id"] = str(response["_id"])
            del response["_id"]
            return response
        return ResponseMessage(success=False, message=f"Role with {id} was not found.")

    async def delete_by_id(self, id: str):
        response = self.validate_id(id)
        if isinstance(response, ResponseMessage):
            return response
        id = response
        response = await self.roles_database.delete_by_id(id)
        if response.deleted_count == 0:
            return ResponseMessage(success=False, message=f"Role with {id} was not found.")
        return ResponseMessage(success=True, message=f"Role with {id} deleted.")

    async def update_by_id(self, id: str, payload: UserRolesResponseModel):
        response = self.validate_id(id)
        if isinstance(response, ResponseMessage):
            return response
        id = response
        where_clouse = {"_id": id}
        already_exist = await self.roles_database.get_by_whereclouse(where_clouse)
        if already_exist:
            where_clouse = {"roleName": payload.role_name}
            dupliacte_exist = await self.roles_database.get_by_whereclouse(where_clouse)
            if str(dupliacte_exist["_id"]) == str(id):
                update_result = await self.roles_database.update_by_id(id, payload)
                if update_result.matched_count  > 0:
                    return payload
            return ResponseMessage(success=False, message="Record already Exist with Name.")
        return ResponseMessage(success=False, message=f"Branch with {id} was not found.")


    async def get_list(self, params: dict):
        skip = (params["page"] - 1) * params["size"]
        order_direction = 1 if params["order_direction"] == "asc" else -1
        params["order_direction"] = order_direction
        params["skip"] = skip
        api_response, total_document = await self.roles_database.get_all(params)
        branches_list_data = UserRolesListResponse()
        branches_list_data.page = params.get("page")
        branches_list_data.size = params.get("size")
        branches_list_data.header_columns = []
        header_column_1 = DataGridHeaderColumn(
            field="company", headerName="Company", description="Company", sequence=0)
        branches_list_data.header_columns.append(
            header_column_1.dict())
        header_column_2 = DataGridHeaderColumn(
            field="branchName", headerName="Branch Name", description="Branch Name", sequence=1)
        branches_list_data.header_columns.append(
            header_column_2.dict())
        
        header_column_3 = DataGridHeaderColumn(
            field="branchCode", headerName="Branch Code", description="Branch Code", sequence=2)
        branches_list_data.header_columns.append(
            header_column_3.dict())
        header_column_4 = DataGridHeaderColumn(
            field="city", headerName="city", description="city", sequence=3)
        branches_list_data.header_columns.append(
            header_column_4.dict())
        header_column_5 = DataGridHeaderColumn(
            field="postalCode", headerName="postalCode", description="postalCode", sequence=4)
        branches_list_data.header_columns.append(
            header_column_5.dict())
        header_column_6 = DataGridHeaderColumn(
            field="phone", headerName="Phone", description="Phone", sequence=5)
        branches_list_data.header_columns.append(
            header_column_6.dict())
        header_column_7 = DataGridHeaderColumn(
            field="fax", headerName="Fax", description="Fax", sequence=6)
        branches_list_data.header_columns.append(
            header_column_7.dict())
        header_column_8 = DataGridHeaderColumn(
            field="licenceNumber", headerName="Licence Number", description="Licence Number", sequence=7)
        branches_list_data.header_columns.append(
            header_column_8.dict())
        header_column_9 = DataGridHeaderColumn(
            field="ntnNumber", headerName="Ntn Number", description="Ntn Number", sequence=8)
        branches_list_data.header_columns.append(
            header_column_9.dict())
        header_column_10 = DataGridHeaderColumn(
            field="iataCode", headerName="Iata Code", description="Iata Code", sequence=9)
        branches_list_data.header_columns.append(
            header_column_10.dict())

        branches_list_data.key_field = {
            "field": "id",
            "templateUrl": "/branches/setup/id"
        }
        branches_list_data.total = total_document["total_no"]
        branches_list_data.items = api_response
        return branches_list_data

    def validate_id(self, id: str):
        try:
            id = PyObjectId(id)
            return id
        except InvalidId as e:
            self.logger.error(e)
            return ResponseMessage(success=False, message=f"Branch id '{id}' is invalid.")