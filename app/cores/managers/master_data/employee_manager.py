from datetime import datetime

from bson.errors import InvalidId
from fastapi.encoders import jsonable_encoder
from app.database.master_data.employee_database import EmployeeDatabase
from app.models.common.common import ResponseMessage
from app.models.common.common_methods import CommonMethodsManager
from app.models.common.data_grid_header_column import DataGridHeaderColumn
from app.models.common.logger import Logger
from app.models.common.py_object_id import PyObjectId
from app.models.master_data.employee_model import EmployeeListResponseModel, EmployeeResponse


class EmployeeManager():
    def __init__(self):
        self.employee_database = EmployeeDatabase()
        self.common_method_manager = CommonMethodsManager()
        self.logger = Logger()

    async def add_employee(self, employee_payload: EmployeeResponse):
        where_clause = {"firstName": employee_payload.first_name, "socialInsuranceNumber": employee_payload.social_insurance_number,
                         "address.province.shortCode": employee_payload.address.province.short_code, "clientId": employee_payload.client_id}
        check_client_exist = await self.employee_database.get_by_where_clause(where_clause)
        if check_client_exist is not None:
            return ResponseMessage(success=False, message="Employee already exists, please choose a different Employee Name.")
        
        employee_payload.created_at = datetime.now()
        response = await self.employee_database.create(employee_payload)

        response_data = EmployeeResponse(**response)
        response_data.id = str(response["id"])
        return response_data

    async def get_employee_details(self, id: str):
        response = self.validate_id(id)
        if isinstance(response, ResponseMessage):
            return response
        id = response
        response = await self.employee_database.get_by_id(id)
        if response:
            db_id = response['_id']
            del response['_id']
            response_data = EmployeeResponse(**response)
            response_data.id = str(db_id)
            return response_data
        return ResponseMessage(success=False, message=f"Employee with {id} was not found.")

    async def delete_by_id(self, id: str):
        response = self.validate_id(id)
        if isinstance(response, ResponseMessage):
            return response
        id = response
        response = await self.employee_database.delete_by_id(id)
        if response.deleted_count == 0:
            return ResponseMessage(success=False, message=f"Employee with {id} was not found.")
        return ResponseMessage(success=True, message=f"Employee with {id} deleted.")

    async def update_by_id(self, id: str, update_model: EmployeeResponse):
        response = self.validate_id(id)
        if isinstance(response, ResponseMessage):
            return response
        id = response
        where_clause = {"firstName": update_model.first_name, "socialInsuranceNumber": update_model.social_insurance_number,
                         "address.province.shortCode": update_model.address.province.short_code, "clientId": update_model.client_id}
        check_employee_exist = await self.employee_database.get_by_where_clause(where_clause)
        if check_employee_exist and check_employee_exist["_id"] != id :
            return ResponseMessage(success=False, message="Employee exists with this Employee Name.")
        
        employee_detail = await self.employee_database.get_by_id(id)
        if employee_detail:

            update_model.created_at = employee_detail["createdAt"]
            update_model.created_by_external_id = employee_detail["createdByExternalId"]
            update_model.created_by_email = employee_detail["createdByEmail"]
            update_model.updated_at = datetime.now()

            update_result = await self.employee_database.update_by_id(id, update_model)
            if update_result.modified_count > 0 or update_result.matched_count == 1:
                update_model.id = str(id)
                try:
                    updated_data = jsonable_encoder(update_model)
                    changed_values = self.common_method_manager.get_nested_changes(employee_detail, updated_data)
                    del changed_values["id"]
                    del changed_values["updatedAt"]
                    if changed_values:
                        changed_values["created_at"] = datetime.now()
                        changed_values["userId"] = update_model.created_by_external_id
                        changed_values["userEmail"] = update_model.created_by_email
                        changed_values["employeeId"] = str(id)
                        response = await self.employee_database.create_employee_log(changed_values)
                except Exception as e:
                    pass
                return update_model
        return ResponseMessage(success=False, message="Employee does not exists.")

    async def get_list(self, params: dict):
        skip = (params["page"] - 1) * params["size"]
        order_direction = 1 if params["order_direction"] == "asc" else -1
        params["order_direction"] = order_direction
        params["skip"] = skip
        api_response, total_document = await self.employee_database.get_all(params)
        employee_list_data = EmployeeListResponseModel()
        employee_list_data.page = params.get("page")
        employee_list_data.size = params.get("size")
        employee_list_data.header_columns = []
        header_column_1 = DataGridHeaderColumn(
            field="empTitle", headerName="Employee Title", description="", sequence=0)
        employee_list_data.header_columns.append(
            header_column_1.dict())
        
        header_column_2 = DataGridHeaderColumn(
            field="firstName", headerName="First Name", description="", sequence=1)
        employee_list_data.header_columns.append(
            header_column_2.dict())
        
        header_column_3 = DataGridHeaderColumn(
            field="lastName", headerName="Last Name", description="", sequence=2)
        employee_list_data.header_columns.append(
            header_column_3.dict())
        
        header_column_4 = DataGridHeaderColumn(
            field="email", headerName="Email", description="", sequence=3)
        employee_list_data.header_columns.append(
            header_column_4.dict())
        
        header_column_5 = DataGridHeaderColumn(
            field="postalCode", headerName="Postal Code", description="", sequence=4)
        employee_list_data.header_columns.append(
            header_column_5.dict())
        
        
        header_column_6 = DataGridHeaderColumn(
            field="city", headerName="City", description="", sequence=5)
        employee_list_data.header_columns.append(
            header_column_6.dict())
        
        header_column_7 = DataGridHeaderColumn(
            field="province", headerName="Province", description="", sequence=6)
        employee_list_data.header_columns.append(
            header_column_7.dict())
        
        header_column_8 = DataGridHeaderColumn(
            field="country", headerName="Country", description="", sequence=7)
        employee_list_data.header_columns.append(
            header_column_8.dict())

        employee_list_data.key_field = {
            "field": "id",
            "templateUrl": "/employee/setup/id"
        }
        employee_list_data.total = total_document["total_no"]
        employee_list_data.items = api_response
        return employee_list_data


    # # helper function to validate the id entered by the user
    def validate_id(self, id: str):
        try:
            id = PyObjectId(id)
            return id
        except InvalidId as e:
            self.logger.error(e)
            return ResponseMessage(success=False, message=f"Employee id '{id}' is invalid.")
        

    async def get_field_detail(self, employee_id: str, field_value: str):
        response = await self.employee_database.get_field_detail(employee_id, field_value)
        if response:
            return response
        return ResponseMessage(success=False, message=f"Result with {employee_id} was not found.")
    

    async def get_ddl_list(self, client_id):
        api_response = await self.employee_database.get_ddl(client_id)
        return api_response
