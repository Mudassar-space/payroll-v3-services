from app.database.master_data.country import CountryDatabase
from app.database.master_data.province import ProvinceDatabase
from app.models.common.common_methods import CommonMethodsManager
from app.models.master_data.province import ProvinceDdlListResponse, ProvinceListResponse, ProvinceRequestPayload, ProvinceResponsePayload
from app.models.common.common import  ResponseMessage
from bson.errors import InvalidId
from app.models.common.data_grid_header_column import DataGridHeaderColumn
from app.models.common.logger import Logger
from app.models.common.py_object_id import PyObjectId



class ProvinceManager():
    def __init__(self) -> None:
        self.province_database = ProvinceDatabase()
        self.country_database = CountryDatabase()
        self.common_method_manager = CommonMethodsManager()
        self.logger = Logger()


    async def create(self, payload: ProvinceRequestPayload):
        response = self.common_method_manager.validate_id(payload.country)
        if isinstance(response, ResponseMessage):
            return response
        country_id = response
        where_clouse = {"_id": country_id}
        country_exist = await self.country_database.get_by_whereclouse(where_clouse)
        if not country_exist:
            return ResponseMessage(success=False, message="Country Not Exist.")
        
        where_clouse = {"name": payload.name}
        already_exist = await self.province_database.get_by_whereclouse(where_clouse)
        if already_exist:
            return ResponseMessage(success=False, message="Record already Exist with Province Name.")
        response = await self.province_database.create(payload)
        return response
    
    async def get_by_id(self, id: str):
        response = self.common_method_manager.validate_id(id)
        if isinstance(response, ResponseMessage):
            return response
        object_id = response
        where_clouse = {"_id": object_id}
        response = await self.province_database.get_by_whereclouse(where_clouse)
        if response:
            response["id"] = str(response["_id"])
            del response["_id"]
            return response
        return ResponseMessage(success=False, message=f"Province with {id} was not found.")

    async def delete_by_id(self, id: str):
        response = self.common_method_manager.validate_id(id)
        if isinstance(response, ResponseMessage):
            return response
        id = response
        response = await self.province_database.delete_by_id(id)
        if response.deleted_count == 0:
            return ResponseMessage(success=False, message=f"Province with {id} was not found.")
        return ResponseMessage(success=True, message=f"Province with {id} deleted.")

    async def update_by_id(self, id: str, payload: ProvinceResponsePayload):
        response = self.common_method_manager.validate_id(payload.country)
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
        where_clouse = {"_id": id}
        already_exist = await self.province_database.get_by_whereclouse(where_clouse)
        if already_exist:
            where_clouse = {"name": already_exist["name"]}
            dupliacte_exist = await self.province_database.get_by_whereclouse(where_clouse)
            if str(dupliacte_exist["_id"]) == str(id):
                update_result = await self.province_database.update_by_id(id, payload)
                if update_result.matched_count  > 0:
                    payload.id = str(id)
                    return payload
            return ResponseMessage(success=False, message="Record already Exist with Name.")
        return ResponseMessage(success=False, message=f"Province with {id} was not found.")


    async def get_list(self, params: dict):
        skip = (params["page"] - 1) * params["size"]
        order_direction = 1 if params["order_direction"] == "asc" else -1
        params["order_direction"] = order_direction
        params["skip"] = skip
        api_response, total_document = await self.province_database.get_all(params)
        province_list_data = ProvinceListResponse()
        province_list_data.page = params.get("page")
        province_list_data.size = params.get("size")
        province_list_data.header_columns = []
        header_column_1 = DataGridHeaderColumn(
            field="name", headerName="Province Name", description="Province Name", sequence=0)
        province_list_data.header_columns.append(
            header_column_1.dict())
        header_column_2 = DataGridHeaderColumn(
            field="shortCode", headerName="short Code", description="shortCode", sequence=1)
        province_list_data.header_columns.append(
            header_column_2.dict())

        province_list_data.key_field = {
            "field": "id",
            "templateUrl": "/province/setup/id"
        }
        province_list_data.total = total_document["total_no"]
        province_list_data.items = api_response
        return province_list_data
    
    
    async def get_ddl_list(self, country_id: str):
        api_response = await self.province_database.get_ddl(country_id)
        return api_response
    