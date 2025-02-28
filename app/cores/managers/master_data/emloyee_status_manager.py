from datetime import datetime
from app.database.master_data.employee_status_database import EmployeeStatusDatabase
from app.models.common.common import  ResponseMessage
from bson.errors import InvalidId
from app.models.common.data_grid_header_column import DataGridHeaderColumn
from app.models.common.logger import Logger
from app.models.common.py_object_id import PyObjectId
from app.models.master_data.employee_status import EmployeeStatusListResponseModel, EmployeeStatusResponsePayload



class EmployeeStatusManager():
    def __init__(self) -> None:
        self.employee_status_database = EmployeeStatusDatabase()
        self.logger = Logger()


    async def create(self, payload: EmployeeStatusResponsePayload):
        where_clause = {"status": payload.employee_status, "clientId":payload.client_id}
        checking_record_exist = await self.employee_status_database.get_by_whereclause(where_clause)
        if checking_record_exist:
            return ResponseMessage(success=False, message="Record already Exist with Status.")
        payload.created_at = datetime.now()
        response = await self.employee_status_database.create(payload)
        return response
    
    async def get_by_id(self, client_id:str, id: str):
        response = self.validate_id(id)
        if isinstance(response, ResponseMessage):
            return response
        object_id = response
        where_clause = {"_id": object_id,
                        'clientId': client_id}
        response = await self.employee_status_database.get_by_whereclause(where_clause)
        if response:
            response["id"] = str(response["_id"])
            del response["_id"]
            return response
        return ResponseMessage(success=False, message=f"Employee Status with this {id} was not found.")

    async def delete_by_id(self,client_id:str, id: str):
        response = self.validate_id(id)
        if isinstance(response, ResponseMessage):
            return response
        id = response
        response = await self.employee_status_database.delete_by_id(client_id, id)
        if response.deleted_count == 0:
            return ResponseMessage(success=False, message=f"Employee Status with this {id} was not found.")
        return ResponseMessage(success=True, message=f"Employee Status with this {id} deleted.")

    async def update_by_id(self, id: str, payload: EmployeeStatusResponsePayload):
        
        response = self.validate_id(id)
        if isinstance(response, ResponseMessage):
            return response
        id = response
        where_clause = {"_id": id}
        already_exist = await self.employee_status_database.get_by_whereclause(where_clause)
        if already_exist:
            where_clause = {"status": payload.employee_status}
            dupliacte_exist = await self.employee_status_database.get_by_whereclause(where_clause)
            if dupliacte_exist:
                if str(dupliacte_exist["_id"]) != str(id):
                    return ResponseMessage(success=False, message="Employee Status exists with this Employee Status Name.")
            
            payload.created_at = already_exist["createdAt"]
            payload.created_by_external_id = already_exist["createdByExternalId"]
            payload.created_by_email = already_exist["createdByEmail"]
            payload.updated_at = datetime.now()
            update_result = await self.employee_status_database.update_by_id(id, payload)
            if update_result.modified_count > 0 or update_result.matched_count == 1:
                payload.id = str(id)
                return payload
        return ResponseMessage(success=False, message=f"Employee Status with {id} was not found.")


    async def get_list(self,client_id:str, params: dict):
        skip = (params["page"] - 1) * params["size"]
        order_direction = 1 if params["order_direction"] == "asc" else -1
        params["order_direction"] = order_direction
        params["skip"] = skip
        api_response, total_document = await self.employee_status_database.get_all(client_id, params)
        returning_list_response_data = EmployeeStatusListResponseModel()
        returning_list_response_data.page = params.get("page")
        returning_list_response_data.size = params.get("size")
        returning_list_response_data.header_columns = []
        header_column_1 = DataGridHeaderColumn(
            field="employeeStatus", headerName="Employee Status", description="", sequence=0)
        returning_list_response_data.header_columns.append(
            header_column_1.dict())
        header_column_2 = DataGridHeaderColumn(
            field="notes", headerName="Notes", description="", sequence=1)
        returning_list_response_data.header_columns.append(
            header_column_2.dict())

        returning_list_response_data.key_field = {
            "field": "id",
            "templateUrl": "/employee-status/setup/id"
        }
        returning_list_response_data.total = total_document["total_no"]
        returning_list_response_data.items = api_response
        return returning_list_response_data
    

    async def get_ddl_list(self, client_id:str):
        api_response = await self.employee_status_database.get_ddl(client_id)
        return api_response
    

    def validate_id(self, id: str):
        try:
            id = PyObjectId(id)
            return id
        except InvalidId as e:
            self.logger.error(e)
            return ResponseMessage(success=False, message=f"Employee Status id '{id}' is invalid.")