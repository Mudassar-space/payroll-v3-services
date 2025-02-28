from datetime import datetime

from bson.errors import InvalidId
from app.database.master_data.accountant_bank_database import AccountantBankDatabase
from app.database.master_data.accountant_database import AccountantDatabase
from app.models.common.common import ResponseMessage
from app.models.common.common_methods import CommonMethodsManager
from app.models.common.data_grid_header_column import DataGridHeaderColumn
from app.models.common.logger import Logger
from app.models.common.py_object_id import PyObjectId
from app.models.master_data.accountant import AccountantListResponseModel, AccountantResponse
from app.models.master_data.accountant_bank import AccountantBankResponse



class AccountantBankManager():
    def __init__(self):
        self.accountant_bank_database = AccountantBankDatabase()
        self.accountant_database = AccountantDatabase()
        self.common_method_manager = CommonMethodsManager()
        self.logger = Logger()

    async def add_bank(self, bank_payload: AccountantBankResponse):
        response = self.common_method_manager.validate_id(bank_payload.accountant_id)
        if isinstance(response, ResponseMessage):
            return response
        id = response
        response = await self.accountant_database.get_by_id(id)
        if not response:
            return ResponseMessage(success=False, message=f"Accountant with {id} was not found.")
        
        where_clouse = {"accountantId": bank_payload.accountant_id, "name": bank_payload.name}
        already_exist = await self.accountant_bank_database.get_by_where_clause(where_clouse)
        if already_exist:
            return ResponseMessage(success=False, message=f"Accountant Bank already exist with name")

        bank_payload.created_at = datetime.now()
        response = await self.accountant_bank_database.create(bank_payload)
        response_data = AccountantBankResponse(**response)
        response_data.id = str(response["id"])
        return response_data

    async def get_bank_details(self, id: str):
        response = self.common_method_manager.validate_id(id)
        if isinstance(response, ResponseMessage):
            return response
        id = response
        response = await self.accountant_bank_database.get_by_id(id)
        if response:
            db_id = response['_id']
            del response['_id']
            response_data = AccountantBankResponse(**response)
            response_data.id = str(db_id)
            return response_data
        return ResponseMessage(success=False, message=f"Accountant Bank with {id} was not found.")

    async def delete_by_id(self, id: str):
        response = self.common_method_manager.validate_id(id)
        if isinstance(response, ResponseMessage):
            return response
        id = response
        response = await self.accountant_bank_database.delete_by_id(id)
        if response.deleted_count == 0:
            return ResponseMessage(success=False, message=f"Accountant Bank with {id} was not found.")
        return ResponseMessage(success=True, message=f"Accountant Bank with {id} deleted.")

    async def update_by_id(self, id: str, update_model: AccountantBankResponse):
        response = self.common_method_manager.validate_id(id)
        if isinstance(response, ResponseMessage):
            return response
        id = response
        accaountant_detail = await self.accountant_bank_database.get_by_id(id)
        if accaountant_detail:
            update_model.created_at = accaountant_detail["createdAt"]
            update_model.created_by_external_id = accaountant_detail["createdByExternalId"]
            update_model.created_by_email = accaountant_detail["createdByEmail"]
            update_model.updated_at = datetime.now()

            update_result = await self.accountant_bank_database.update_by_id(id, update_model)
            if update_result.modified_count > 0 or update_result.matched_count == 1:
                update_model.id = str(id)
                return update_model
        return ResponseMessage(success=False, message="Accountant Bank does not exists.")

    async def get_list(self, accountant_id: str, params: dict):
        skip = (params["page"] - 1) * params["size"]
        order_direction = 1 if params["order_direction"] == "asc" else -1
        params["order_direction"] = order_direction
        params["skip"] = skip
        api_response = await self.accountant_bank_database.get_all(accountant_id, params)
        accountant_list_data = AccountantListResponseModel()
        accountant_list_data.page = params.get("page")
        accountant_list_data.size = params.get("size")
        accountant_list_data.header_columns = []
        header_column_1 = DataGridHeaderColumn(
            field="accTitle", headerName="Accountant Title", description="", sequence=0)
        accountant_list_data.header_columns.append(
            header_column_1.dict())
        
        header_column_2 = DataGridHeaderColumn(
            field="firstName", headerName="First Name", description="", sequence=1)
        accountant_list_data.header_columns.append(
            header_column_2.dict())
        
        header_column_3 = DataGridHeaderColumn(
            field="lastName", headerName="Last Name", description="", sequence=2)
        accountant_list_data.header_columns.append(
            header_column_3.dict())
        
        header_column_4 = DataGridHeaderColumn(
            field="email", headerName="Email", description="", sequence=3)
        accountant_list_data.header_columns.append(
            header_column_4.dict())
        
        header_column_5 = DataGridHeaderColumn(
            field="postalCode", headerName="Postal Code", description="", sequence=4)
        accountant_list_data.header_columns.append(
            header_column_5.dict())
        
        
        header_column_6 = DataGridHeaderColumn(
            field="city", headerName="City", description="", sequence=5)
        accountant_list_data.header_columns.append(
            header_column_6.dict())
        
        header_column_7 = DataGridHeaderColumn(
            field="province", headerName="Province", description="", sequence=6)
        accountant_list_data.header_columns.append(
            header_column_7.dict())
        
        header_column_8 = DataGridHeaderColumn(
            field="country", headerName="Country", description="", sequence=7)
        accountant_list_data.header_columns.append(
            header_column_8.dict())

        accountant_list_data.key_field = {
            "field": "id",
            "templateUrl": "/accountant/setup/id"
        }
        accountant_list_data.total = api_response["total_count"]
        accountant_list_data.items = api_response["data"]
        return accountant_list_data
    

    async def get_ddl_list(self, accountant_id):
        api_response = await self.accountant_bank_database.get_ddl(accountant_id)
        return api_response
