from datetime import datetime

from bson.errors import InvalidId
from fastapi.encoders import jsonable_encoder
from app.database.master_data.accountant_database import AccountantDatabase
from app.database.master_data.client_database import ClientDatabase
from app.models.common.common import ResponseMessage
from app.models.common.common_methods import CommonMethodsManager
from app.models.common.data_grid_header_column import DataGridHeaderColumn
from app.models.common.logger import Logger
from app.models.common.py_object_id import PyObjectId
from app.models.master_data.client_model import ClientListResponseModel, ClientResponse


class ClientManager():
    def __init__(self):
        self.client_database = ClientDatabase()
        self.common_method_manager = CommonMethodsManager()
        self.accountant_database = AccountantDatabase()
        self.logger = Logger()

    async def add_client(self, client_payload: ClientResponse):
        if client_payload.accountant_id != None:
            accountant_id = self.common_method_manager.validate_id(client_payload.accountant_id)
            if isinstance(accountant_id, ResponseMessage):
                return accountant_id
            accountant_obj_id = accountant_id
            where_clouse = {"_id": accountant_obj_id}
            check_acc_exist = await self.accountant_database.get_by_where_clause(where_clouse)
            if not check_acc_exist:
                return ResponseMessage(success=False, message="Accountant not found with this id.")
            if check_acc_exist and check_acc_exist["activateAccount"] != True:
                return ResponseMessage(success=False, message="Accountant not in active state")
        else:
            where_clouse = {"defaultAccountant": True, "activateAccount": True}
            check_acc_exist = await self.accountant_database.get_by_where_clause(where_clouse)
            client_payload.accountant_id = str(check_acc_exist["_id"])
        where_clause = {"legal_name": client_payload.legal_name}
        check_client_exist = await self.client_database.get_by_where_clause(where_clause)
        if check_client_exist is not None:
            return ResponseMessage(success=False, message="Client already exists, please choose a different client Name.")
        
        client_payload.created_at = datetime.now()
        response = await self.client_database.create(client_payload)

        response_data = ClientResponse(**response)
        response_data.id = str(response["id"])
        return response_data

    async def get_client_details(self, id: str):
        response = self.common_method_manager.validate_id(id)
        if isinstance(response, ResponseMessage):
            return response
        id = response
        response = await self.client_database.get_by_id(id)
        if response:
            db_id = response['_id']
            del response['_id']
            response_data = ClientResponse(**response)
            response_data.id = str(db_id)
            return response_data
        return ResponseMessage(success=False, message=f"Client with {id} was not found.")

    async def delete_by_id(self, id: str):
        response = self.common_method_manager.validate_id(id)
        if isinstance(response, ResponseMessage):
            return response
        id = response
        response = await self.client_database.delete_by_id(id)
        if response.deleted_count == 0:
            return ResponseMessage(success=False, message=f"Client with {id} was not found.")
        return ResponseMessage(success=True, message=f"Client with {id} deleted.")

    async def update_by_id(self, id: str, update_model: ClientResponse):
        response = self.common_method_manager.validate_id(id)
        if isinstance(response, ResponseMessage):
            return response
        id = response
        where_clause = {"legal_name": update_model.legal_name, "accountantId": update_model.accountant_id}
        check_client_exist = await self.client_database.get_by_where_clause(where_clause)
        if check_client_exist and check_client_exist["_id"] != id :
            return ResponseMessage(success=False, message="Client exists with this Client Name.")
        
        client_detail = await self.client_database.get_by_id(id)
        if client_detail:

            update_model.created_at = client_detail["createdAt"]
            update_model.created_by_external_id = client_detail["createdByExternalId"]
            update_model.created_by_email = client_detail["createdByEmail"]
            update_model.updated_at = datetime.now()

            update_result = await self.client_database.update_by_id(id, update_model)
            if update_result.modified_count > 0 or update_result.matched_count == 1:
                update_model.id = str(id)
                try:
                    updated_data = jsonable_encoder(update_model)
                    changed_values = self.common_method_manager.get_nested_changes(client_detail, updated_data)
                    del changed_values["id"]
                    del changed_values["updatedAt"]
                    if changed_values:
                        changed_values["created_at"] = datetime.now()
                        changed_values["userId"] = update_model.created_by_external_id
                        changed_values["userEmail"] = update_model.created_by_email
                        changed_values["clientId"] = str(id)
                        response = await self.client_database.create_client_log(changed_values)
                except Exception as e:
                    pass
                return update_model
        return ResponseMessage(success=False, message="Client does not exists.")

    async def get_list(self, accountant_id: str, params: dict):
        skip = (params["page"] - 1) * params["size"]
        order_direction = 1 if params["order_direction"] == "asc" else -1
        params["order_direction"] = order_direction
        params["skip"] = skip
        api_response = await self.client_database.get_all(accountant_id, params)
        client_list_data = ClientListResponseModel()
        client_list_data.page = params.get("page")
        client_list_data.size = params.get("size")
        client_list_data.header_columns = []
        header_column_1 = DataGridHeaderColumn(
            field="accTitle", headerName="Accountant Title", description="", sequence=0)
        client_list_data.header_columns.append(
            header_column_1.dict())
        
        header_column_2 = DataGridHeaderColumn(
            field="firstName", headerName="First Name", description="", sequence=1)
        client_list_data.header_columns.append(
            header_column_2.dict())
        
        header_column_3 = DataGridHeaderColumn(
            field="lastName", headerName="Last Name", description="", sequence=2)
        client_list_data.header_columns.append(
            header_column_3.dict())
        
        header_column_4 = DataGridHeaderColumn(
            field="email", headerName="Email", description="", sequence=3)
        client_list_data.header_columns.append(
            header_column_4.dict())
        
        header_column_5 = DataGridHeaderColumn(
            field="postalCode", headerName="Postal Code", description="", sequence=4)
        client_list_data.header_columns.append(
            header_column_5.dict())
        
        
        header_column_6 = DataGridHeaderColumn(
            field="city", headerName="City", description="", sequence=5)
        client_list_data.header_columns.append(
            header_column_6.dict())
        
        header_column_7 = DataGridHeaderColumn(
            field="province", headerName="Province", description="", sequence=6)
        client_list_data.header_columns.append(
            header_column_7.dict())
        
        header_column_8 = DataGridHeaderColumn(
            field="country", headerName="Country", description="", sequence=7)
        client_list_data.header_columns.append(
            header_column_8.dict())

        client_list_data.key_field = {
            "field": "id",
            "templateUrl": "/client/setup/id"
        }
        client_list_data.total = api_response["total_count"]
        client_list_data.items = api_response["data"]
        return client_list_data
        

    async def get_field_detail(self, client_id: str, field_value: str):
        response = await self.client_database.get_field_detail(client_id, field_value)
        if response:
            return response
        return ResponseMessage(success=False, message=f"Result with {client_id} was not found.")
    

    async def move_client(self, accountant_id: str, client_ids: str):
        try:
            for client_id in client_ids:
                response = self.common_method_manager.validate_id(client_id)
                if isinstance(response, ResponseMessage):
                    return response
                id = response     
                client_detail = await self.client_database.get_by_id(id)
                if client_detail:

                    client_detail["accountantId"] = str(accountant_id)
                    client_detail["updatedAt"] = datetime.now()
                    client_detail["id"] = "string"
                    del client_detail["_id"]
                    update_result = await self.client_database.update_by_id(id, client_detail)
                    if update_result.modified_count > 0 or update_result.matched_count == 1:
                        pass
            return ResponseMessage(success=True, message="Clients moved successfully.")
        except Exception as e :
            return ResponseMessage(success=False, message="Client does not exists.")
    

    async def get_ddl_list(self, accountant_id):
        api_response = await self.client_database.get_ddl(accountant_id)
        return api_response
   
