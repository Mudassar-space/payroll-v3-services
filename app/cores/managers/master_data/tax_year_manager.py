from datetime import datetime
from app.database.master_data.client_database import ClientDatabase
from app.database.master_data.tax_year_database import TaxYearDatabase
from app.models.common.common_methods import CommonMethodsManager
from app.models.common.common import  ResponseMessage
from app.models.common.data_grid_header_column import DataGridHeaderColumn
from app.models.common.logger import Logger
from app.models.master_data.tax_year import TaxYearListResponseModel, TaxYearResponsePayload
from app.models.master_data.designation import DesignationListResponseModel, DesignationResponsePayload
from app.models.master_data.tax_year import TaxYearResponsePayload



class TaxYearManager():
    def __init__(self) -> None:
        self.tax_year_database = TaxYearDatabase()
        self.common_method_manager = CommonMethodsManager()
        self.logger = Logger()


    async def create(self, payload: TaxYearResponsePayload):
        where_clouse = {"taxYear": payload.tax_year}
        check_tax_year_exist = await self.tax_year_database.get_by_where_clause(where_clouse)
        if check_tax_year_exist:
            return ResponseMessage(success=False, message="Tax Year already exists.")
        payload.created_at = datetime.now()
        response = await self.tax_year_database.create(payload)
        return response
    
    async def get_by_id(self, id: str):
        response = self.common_method_manager.validate_id(id)
        if isinstance(response, ResponseMessage):
            return response
        id = response
        where_clause = {"_id": id}
        response = await self.tax_year_database.get_by_where_clause(where_clause)
        if response:
            response["id"] = str(response["_id"])
            del response["_id"]
            return response
        return ResponseMessage(success=False, message=f"Tax Year with this {id} was not found.")

    async def delete_by_id(self, id: str):
        response = self.common_method_manager.validate_id(id)
        if isinstance(response, ResponseMessage):
            return response
        id = response
        response = await self.tax_year_database.delete_by_id(id)
        if response.deleted_count == 0:
            return ResponseMessage(success=False, message=f"Tax Year with this {id} was not found.")
        return ResponseMessage(success=True, message=f"Tax Year with this {id} deleted.")

    async def update_by_id(self, id: str, payload: TaxYearResponsePayload):
        response = self.common_method_manager.validate_id(id)
        if isinstance(response, ResponseMessage):
            return response
        id = response
        where_clouse = {"_id": id}
        already_exist = await self.tax_year_database.get_by_where_clause(where_clouse)
        if already_exist:
            where_clouse = {"taxYear": already_exist["taxYear"]}
            dupliacte_exist = await self.tax_year_database.get_by_where_clause(where_clouse)
            if str(dupliacte_exist["_id"]) == str(id):
                payload.created_at = already_exist["createdAt"]
                payload.created_by_external_id = already_exist["createdByExternalId"]
                payload.created_by_email = already_exist["createdByEmail"]
                payload.updated_at = datetime.now()
                update_result = await self.tax_year_database.update_by_id(id, payload)
                if update_result.matched_count  > 0:
                    payload.id = str(id)
                    return payload
            return ResponseMessage(success=False, message="Record already Exist with Tax Year.")
        return ResponseMessage(success=False, message=f"Tax Year with {id} was not found.")


    async def get_list(self, params: dict):
        skip = (params["page"] - 1) * params["size"]
        order_direction = 1 if params["order_direction"] == "asc" else -1
        params["order_direction"] = order_direction
        params["skip"] = skip
        api_response, total_document = await self.tax_year_database.get_all(params)
        tax_year_list_data = TaxYearListResponseModel()
        tax_year_list_data.page = params.get("page")
        tax_year_list_data.size = params.get("size")
        tax_year_list_data.header_columns = []
        header_column_1 = DataGridHeaderColumn(
            field="taxYear", headerName="Tax Year", description="", sequence=0)
        tax_year_list_data.header_columns.append(
            header_column_1.dict())

        tax_year_list_data.key_field = {
            "field": "id",
            "templateUrl": "/TaxYear/setup/id"
        }
        tax_year_list_data.total = total_document["total_no"]
        tax_year_list_data.items = api_response
        return tax_year_list_data
    

    async def get_ddl_list(self):
        api_response = await self.tax_year_database.get_ddl()
        return api_response
