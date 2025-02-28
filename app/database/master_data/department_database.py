import asyncio
from bson import ObjectId
from app.config.config import DATABASE_NAME, MONGODB_CON_STR
from fastapi.encoders import jsonable_encoder
from motor.motor_asyncio import AsyncIOMotorClient

from app.models.common.ddl_entity import DDLEntity
from app.models.master_data.departments import DepartmentListModel, DepartmentResponsePayload
from app.models.master_data.province import ProvinceDdlResponsePayload, ProvinceRequestPayload, ProvinceResponsePayload


class DepartmentDatabase():
    client = AsyncIOMotorClient(MONGODB_CON_STR)
    client.get_io_loop = asyncio.get_running_loop
    department_collection = client[DATABASE_NAME]["departments"]


    async def create(self, payload: DepartmentResponsePayload):
        document = jsonable_encoder(payload)
        del document["id"]
        del document["updatedAt"]
        del document["updatedByEmail"]
        del document["updatedByExternalId"]
        result = await self.department_collection.insert_one(document)
        document["id"] = str(result.inserted_id)
        del document["_id"]
        return document
    
    def get_by_whereclause(self, where_clause):
        return self.department_collection.find_one(where_clause)
    
    async def delete_by_id(self,id: ObjectId):
        return await self.department_collection.delete_one({"_id": id})

    async def update_by_id(self, id: ObjectId, payload: DepartmentResponsePayload):
        update_request_payload = jsonable_encoder(
            payload)
        del update_request_payload["id"]
        del update_request_payload["createdAt"]
        del update_request_payload["createdByEmail"]
        del update_request_payload["createdByExternalId"]
        result = await self.department_collection.update_one({"_id": id}, {"$set": update_request_payload})
        return result

    async def get_all(self, client_id: str, params):
        department_list = []
        filter = {"clientId": str(client_id)}
        if len(params["search_query"]) > 0:
            filter = {
                "departmentName": {'$regex': params['search_query'],  '$options': 'i'},
                "clientId": str(client_id)
            }
        cursor = self.department_collection.find(filter, {"departmentName": 1, "notes": 1}).sort(
            params["order_by"], params["order_direction"]).skip(params["skip"]).limit(params["size"])
        async for document in cursor:
            document["id"] = str(document["_id"])
            del document["_id"]
            department_list.append(document)
            
        total_count =await self.department_collection.aggregate([{
                "$match": {"clientId": str(client_id)}},
                {
                "$count": "total_no"
                }
                ]).to_list(None)
        if  len(total_count) == 0:
            total_document = {"total_no": 0}
        else: 
            total_document = total_count[0]
       
        return department_list, total_document
    

    async def get_ddl(self, client_id:str):
        designation_ddl =await self.department_collection.aggregate([
            {
                "$match":{
                    "clientId":client_id,
                    },
        },
        {
                 "$project":{
                    "_id": 0,
                    "label": "$departmentName",
                    "value": {"$toString": "$_id"}
                 }}   
                ]).to_list(None)
        return designation_ddl
    