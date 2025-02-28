from datetime import datetime
from app.database.master_data.client_database import ClientDatabase
from app.database.master_data.deduction_database import DeductionDatabase
from app.models.common.common_methods import CommonMethodsManager
from app.models.common.common import  ResponseMessage
from app.models.common.data_grid_header_column import DataGridHeaderColumn
from app.models.common.logger import Logger
from app.models.master_data.deduction import DeductionListResponseModel, DeductionResponsePayload
from app.models.master_data.designation import DesignationListResponseModel, DesignationResponsePayload



class DeductionManager():
    def __init__(self) -> None:
        self.deduction_database = DeductionDatabase()
        self.common_method_manager = CommonMethodsManager()
        self.client_database = ClientDatabase()
        
        self.logger = Logger()


    async def create(self, payload: DeductionResponsePayload):
        response = self.common_method_manager.validate_id(payload.client_id)
        if isinstance(response, ResponseMessage):
            return response
        id = response
        response = await self.client_database.get_by_id(id)
        if response == None:
            return ResponseMessage(success=False, message=f"Client id with this {id} was not found.")
        payload.created_at = datetime.now()
        response = await self.deduction_database.create(payload)
        return response
    
    async def get_by_id(self, id: str):
        response = self.common_method_manager.validate_id(id)
        if isinstance(response, ResponseMessage):
            return response
        id = response
        where_clause = {"_id": id}
        response = await self.deduction_database.get_by_whereclause(where_clause)
        if response:
            response["id"] = str(response["_id"])
            del response["_id"]
            return response
        return ResponseMessage(success=False, message=f"Deduction with this {id} was not found.")

    async def delete_by_id(self, id: str):
        response = self.common_method_manager.validate_id(id)
        if isinstance(response, ResponseMessage):
            return response
        id = response
        response = await self.deduction_database.delete_by_id(id)
        if response.deleted_count == 0:
            return ResponseMessage(success=False, message=f"Deduction with this {id} was not found.")
        return ResponseMessage(success=True, message=f"Deduction with this {id} deleted.")

    async def update_by_id(self, id: str, payload: DeductionResponsePayload):
        
        response = self.common_method_manager.validate_id(id)
        if isinstance(response, ResponseMessage):
            return response
        id = response
        where_clause = {"_id": id, "clientId": payload.client_id}
        already_exist = await self.deduction_database.get_by_whereclause(where_clause)
        if already_exist:
            payload.created_at = already_exist["createdAt"]
            payload.created_by_external_id = already_exist["createdByExternalId"]
            payload.created_by_email = already_exist["createdByEmail"]
            payload.updated_at = datetime.now()
            update_result = await self.deduction_database.update_by_id(id, payload)
            if update_result.modified_count > 0 or update_result.matched_count == 1:
                payload.id = str(id)
                return payload
        return ResponseMessage(success=False, message=f"Deduction with {id} was not found.")


    async def get_list(self, client_id:str,params: dict):
        skip = (params["page"] - 1) * params["size"]
        order_direction = 1 if params["order_direction"] == "asc" else -1
        params["order_direction"] = order_direction
        params["skip"] = skip
        api_response, total_document = await self.deduction_database.get_all(client_id, params)
        deduction_list_data = DeductionListResponseModel()
        deduction_list_data.page = params.get("page")
        deduction_list_data.size = params.get("size")
        deduction_list_data.header_columns = []
        header_column_1 = DataGridHeaderColumn(
            field="label", headerName="Deduction Label", description="", sequence=0)
        deduction_list_data.header_columns.append(
            header_column_1.dict())
        header_column_2 = DataGridHeaderColumn(
            field="showInPayroll", headerName="Show In Payroll", description="", sequence=1)
        deduction_list_data.header_columns.append(
            header_column_2.dict())

        deduction_list_data.key_field = {
            "field": "id",
            "templateUrl": "/Deduction/setup/id"
        }
        deduction_list_data.total = total_document["total_no"]
        deduction_list_data.items = api_response
        return deduction_list_data
    

    async def get_ddl_list(self, client_id):
        api_response = await self.deduction_database.get_ddl(client_id)
        return api_response
