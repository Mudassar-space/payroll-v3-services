from datetime import datetime
from app.database.master_data.department_database import DepartmentDatabase
from app.models.common.common_methods import CommonMethodsManager
from app.models.master_data.departments import DepartmentListResponseModel, DepartmentResponsePayload
from app.models.common.common import  ResponseMessage
from bson.errors import InvalidId
from app.models.common.data_grid_header_column import DataGridHeaderColumn
from app.models.common.logger import Logger
from app.models.common.py_object_id import PyObjectId



class DepartmentManager():
    def __init__(self) -> None:
        self.department_database = DepartmentDatabase()
        self.common_method_manager = CommonMethodsManager()
        self.logger = Logger()


    async def create(self, payload: DepartmentResponsePayload):
        where_clause = {"departmentName": payload.department_name, "clientId":payload.client_id}
        department_exist = await self.department_database.get_by_whereclause(where_clause)
        if department_exist:
            return ResponseMessage(success=False, message="Record already Exist with Department Name.")
        payload.created_at = datetime.now()
        response = await self.department_database.create(payload)
        return response
    
    async def get_by_id(self, client_id:str, id: str):
        response = self.common_method_manager.validate_id(id)
        if isinstance(response, ResponseMessage):
            return response
        object_id = response
        where_clause = {"_id": object_id}
        response = await self.department_database.get_by_whereclause(where_clause)
        if response:
            response["id"] = str(response["_id"])
            del response["_id"]
            return response
        return ResponseMessage(success=False, message=f"Department with this {id} was not found.")

    async def delete_by_id(self, id: str):
        response = self.common_method_manager.validate_id(id)
        if isinstance(response, ResponseMessage):
            return response
        id = response
        response = await self.department_database.delete_by_id(id)
        if response.deleted_count == 0:
            return ResponseMessage(success=False, message=f"Department with this {id} was not found.")
        return ResponseMessage(success=True, message=f"Department with this {id} deleted.")

    async def update_by_id(self, id: str, payload: DepartmentResponsePayload):
        
        response = self.common_method_manager.validate_id(id)
        if isinstance(response, ResponseMessage):
            return response
        id = response
        where_clause = {"_id": id}
        already_exist = await self.department_database.get_by_whereclause(where_clause)
        if already_exist:
            where_clause = {"departmentName": payload.department_name}
            dupliacte_exist = await self.department_database.get_by_whereclause(where_clause)
            if dupliacte_exist:
                if str(dupliacte_exist["_id"]) != str(id):
                    return ResponseMessage(success=False, message="Department exists with this Department Name.")
            
            payload.created_at = already_exist["createdAt"]
            payload.created_by_external_id = already_exist["createdByExternalId"]
            payload.created_by_email = already_exist["createdByEmail"]
            payload.updated_at = datetime.now()
            update_result = await self.department_database.update_by_id(id, payload)
            if update_result.modified_count > 0 or update_result.matched_count == 1:
                payload.id = str(id)
                return payload
        return ResponseMessage(success=False, message=f"Department with {id} was not found.")


    async def get_list(self,client_id:str, params: dict):
        skip = (params["page"] - 1) * params["size"]
        order_direction = 1 if params["order_direction"] == "asc" else -1
        params["order_direction"] = order_direction
        params["skip"] = skip
        api_response, total_document = await self.department_database.get_all(client_id, params)
        department_list_data = DepartmentListResponseModel()
        department_list_data.page = params.get("page")
        department_list_data.size = params.get("size")
        department_list_data.header_columns = []
        header_column_1 = DataGridHeaderColumn(
            field="departmentName", headerName="Department Name", description="", sequence=0)
        department_list_data.header_columns.append(
            header_column_1.dict())
        header_column_2 = DataGridHeaderColumn(
            field="notes", headerName="Notes", description="", sequence=1)
        department_list_data.header_columns.append(
            header_column_2.dict())

        department_list_data.key_field = {
            "field": "id",
            "templateUrl": "/department/setup/id"
        }
        department_list_data.total = total_document["total_no"]
        department_list_data.items = api_response
        return department_list_data
    

    async def get_ddl_list(self, client_id:str):
        api_response = await self.department_database.get_ddl(client_id)
        return api_response
    