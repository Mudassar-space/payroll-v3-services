from datetime import datetime
from app.database.master_data.payroll_frequencies_database import PayrollFrequenciesDatabase
from app.models.common.common_methods import CommonMethodsManager
from app.models.common.common import  ResponseMessage
from app.models.common.data_grid_header_column import DataGridHeaderColumn
from app.models.common.logger import Logger
from app.models.master_data.payroll_frequencies import PayrollFrequenciesListResponseModel, PayrollFrequenciesResponsePayload
from app.models.master_data.tax_year import TaxYearListResponseModel, TaxYearResponsePayload
from app.models.master_data.tax_year import TaxYearResponsePayload



class PayrollFrequenciesManager():
    def __init__(self) -> None:
        self.payroll_frequencies_database = PayrollFrequenciesDatabase()
        self.common_method_manager = CommonMethodsManager()
        self.logger = Logger()


    async def create(self, payload: PayrollFrequenciesResponsePayload):
        where_clouse = {"label": payload.label}
        check_payroll_freq_exist = await self.payroll_frequencies_database.get_by_where_clause(where_clouse)
        if check_payroll_freq_exist:
            return ResponseMessage(success=False, message="Payroll Frequencies already exists.")
        payload.created_at = datetime.now()
        response = await self.payroll_frequencies_database.create(payload)
        return response
    
    async def get_by_id(self, id: str):
        response = self.common_method_manager.validate_id(id)
        if isinstance(response, ResponseMessage):
            return response
        id = response
        where_clause = {"_id": id}
        response = await self.payroll_frequencies_database.get_by_where_clause(where_clause)
        if response:
            response["id"] = str(response["_id"])
            del response["_id"]
            return response
        return ResponseMessage(success=False, message=f"Payroll Frequencies with this {id} was not found.")

    async def delete_by_id(self, id: str):
        response = self.common_method_manager.validate_id(id)
        if isinstance(response, ResponseMessage):
            return response
        id = response
        response = await self.payroll_frequencies_database.delete_by_id(id)
        if response.deleted_count == 0:
            return ResponseMessage(success=False, message=f"Payroll Frequencies with this {id} was not found.")
        return ResponseMessage(success=True, message=f"Payroll Frequencies with this {id} deleted.")

    async def update_by_id(self, id: str, payload: PayrollFrequenciesResponsePayload):
        response = self.common_method_manager.validate_id(id)
        if isinstance(response, ResponseMessage):
            return response
        id = response
        where_clouse = {"_id": id}
        already_exist = await self.payroll_frequencies_database.get_by_where_clause(where_clouse)
        if already_exist:
            where_clouse = {"label": already_exist["label"]}
            dupliacte_exist = await self.payroll_frequencies_database.get_by_where_clause(where_clouse)
            if str(dupliacte_exist["_id"]) == str(id):
                payload.created_at = already_exist["createdAt"]
                payload.created_by_external_id = already_exist["createdByExternalId"]
                payload.created_by_email = already_exist["createdByEmail"]
                payload.updated_at = datetime.now()
                update_result = await self.payroll_frequencies_database.update_by_id(id, payload)
                if update_result.matched_count  > 0:
                    payload.id = str(id)
                    return payload
            return ResponseMessage(success=False, message="Record already Exist with Payroll Frequencies.")
        return ResponseMessage(success=False, message=f"Payroll Frequencies with {id} was not found.")


    async def get_list(self, params: dict):
        skip = (params["page"] - 1) * params["size"]
        order_direction = 1 if params["order_direction"] == "asc" else -1
        params["order_direction"] = order_direction
        params["skip"] = skip
        api_response, total_document = await self.payroll_frequencies_database.get_all(params)
        payroll_freq_list_data = PayrollFrequenciesListResponseModel()
        payroll_freq_list_data.page = params.get("page")
        payroll_freq_list_data.size = params.get("size")
        payroll_freq_list_data.header_columns = []
        header_column_1 = DataGridHeaderColumn(
            field="label", headerName="Payroll Frequencies", description="", sequence=0)
        payroll_freq_list_data.header_columns.append(
            header_column_1.dict())

        payroll_freq_list_data.key_field = {
            "field": "id",
            "templateUrl": "/label/setup/id"
        }
        payroll_freq_list_data.total = total_document["total_no"]
        payroll_freq_list_data.items = api_response
        return payroll_freq_list_data
    

    async def get_ddl_list(self):
        api_response = await self.payroll_frequencies_database.get_ddl()
        return api_response
