from datetime import datetime

from bson.errors import InvalidId
from fastapi.encoders import jsonable_encoder
from app.database.master_data.accountant_database import AccountantDatabase
from app.database.master_data.country import CountryDatabase
from app.models.common.common import ResponseMessage
from app.models.common.common_methods import CommonMethodsManager
from app.models.common.data_grid_header_column import DataGridHeaderColumn
from app.models.common.logger import Logger
from app.models.common.py_object_id import PyObjectId
from app.models.master_data.accountant import AccountantListResponseModel, AccountantResponse


class AccountantManager():
    def __init__(self):
        self.accountant_database = AccountantDatabase()
        self.common_method_manager = CommonMethodsManager()
        self.country_database = CountryDatabase()
        self.country_database = CountryDatabase()
        self.logger = Logger()

    async def add_accountant(self, accountant_payload: AccountantResponse):
        
        response = self.common_method_manager.validate_id(accountant_payload.address.country.id)
        if isinstance(response, ResponseMessage):
            return response
        country_id = response
        where_clouse = {"_id": country_id}
        country_exist = await self.country_database.get_by_whereclouse(where_clouse)
        if not country_exist:
            return ResponseMessage(success=False, message="Country Not Exist.")
        

        where_clause = {"accTitle": accountant_payload.acc_title}
        check_acc_exist = await self.accountant_database.get_by_where_clause(where_clause)
        if check_acc_exist is not None:
            return ResponseMessage(success=False, message="Accountant already exists, please choose a different Account Title.")
        
        accountant_payload.created_at = datetime.now()
        response = await self.accountant_database.create(accountant_payload)

        response_data = AccountantResponse(**response)
        response_data.id = str(response["id"])
        return response_data

    async def get_accountant_details(self, id: str):
        response = self.common_method_manager.validate_id(id)
        if isinstance(response, ResponseMessage):
            return response
        id = response
        response = await self.accountant_database.get_by_id(id)
        if response:
            db_id = response['_id']
            del response['_id']
            response_data = AccountantResponse(**response)
            response_data.id = str(db_id)
            return response_data
        return ResponseMessage(success=False, message=f"Accountant with {id} was not found.")
    

    async def delete_by_id(self, id: str):
        response = self.common_method_manager.validate_id(id)
        if isinstance(response, ResponseMessage):
            return response
        id = response
        response = await self.accountant_database.delete_by_id(id)
        if response.deleted_count == 0:
            return ResponseMessage(success=False, message=f"Accountant with {id} was not found.")
        return ResponseMessage(success=True, message=f"Accountant with {id} deleted.")


    async def update_by_id(self, id: str, update_model: AccountantResponse):

        response = self.common_method_manager.validate_id(update_model.address.country.id)
        if isinstance(response, ResponseMessage):
            return response
        country_id = response
        where_clouse = {"_id": country_id}
        country_exist = await self.country_database.get_by_whereclouse(where_clouse)
        if not country_exist:
            return ResponseMessage(success=False, message="Country Not Exist.")
        
        response = self.common_method_manager.validate_id(id)
        if isinstance(response, ResponseMessage):
            return response
        id = response
        where_clause = {"accTitle": update_model.acc_title}
        check_acc_exist = await self.accountant_database.get_by_where_clause(where_clause)
        if check_acc_exist and check_acc_exist["_id"] != id :
            return ResponseMessage(success=False, message="Accountant exists with this Accountant Title.")
        
        accaountant_detail = await self.accountant_database.get_by_id(id)
        if accaountant_detail:

            update_model.created_at = accaountant_detail["createdAt"]
            update_model.created_by_external_id = accaountant_detail["createdByExternalId"]
            update_model.created_by_email = accaountant_detail["createdByEmail"]
            update_model.updated_at = datetime.now()

            update_result = await self.accountant_database.update_by_id(id, update_model)
            if update_result.modified_count > 0 or update_result.matched_count == 1:
                update_model.id = str(id)
                try:
                    updated_data = jsonable_encoder(update_model)
                    changed_values = self.common_method_manager.get_nested_changes(accaountant_detail, updated_data)
                    del changed_values["id"]
                    del changed_values["updatedAt"]
                    if changed_values:
                        changed_values["created_at"] = datetime.now()
                        changed_values["userId"] = update_model.created_by_external_id
                        changed_values["userEmail"] = update_model.created_by_email
                        changed_values["accountId"] = str(id)
                        response = await self.accountant_database.create_accountant_log(changed_values)
                except Exception as e:
                    pass
                return update_model
        return ResponseMessage(success=False, message="Accountant does not exists.")

    async def get_list(self, params: dict):
        skip = (params["page"] - 1) * params["size"]
        order_direction = 1 if params["order_direction"] == "asc" else -1
        params["order_direction"] = order_direction
        params["skip"] = skip
        api_response = await self.accountant_database.get_all(params)
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
    

    async def get_field_detail(self, accountant_id: str, field_value: str):
        response = await self.accountant_database.get_field_detail(accountant_id, field_value)
        if response:
            return response
        return ResponseMessage(success=False, message=f"Result with {accountant_id} was not found.")
    

    async def get_ddl_list(self):
        api_response = await self.accountant_database.get_ddl()
        return api_response



        

