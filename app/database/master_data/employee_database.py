import asyncio

from bson.objectid import ObjectId
from fastapi.encoders import jsonable_encoder
from motor.motor_asyncio import AsyncIOMotorClient

from app.config.config import DATABASE_NAME, MONGODB_CON_STR
from app.models.common.ddl_entity import DDLEntity
from app.models.master_data.employee_model import EmployeeResponse, EmployeeReuestPayload


class EmployeeDatabase():
    client = AsyncIOMotorClient(MONGODB_CON_STR)
    client.get_io_loop = asyncio.get_running_loop
    employee_collection = client[DATABASE_NAME]["employee"]
    employee_log_collection = client[DATABASE_NAME]["employee_log"]

    async def create(self, document: EmployeeResponse):
        document = jsonable_encoder(document)
        del document["id"]
        # Removed update fields during the add operation
        del document["updatedAt"]
        del document["updatedByEmail"]
        del document["updatedByExternalId"]
        result = await self.employee_collection.insert_one(document)
        document["id"] = result.inserted_id
        return document
    
    async def create_employee_log(self, document: dict):
        result = await self.employee_log_collection.insert_one(document)
        return document

    async def get_by_where_clause(self, where_clause: dict):
        return await self.employee_collection.find_one(where_clause)

    async def get_by_id(self, id: ObjectId):
        return await self.employee_collection.find_one({"_id": id})

    async def delete_by_id(self, id: ObjectId):
        return await self.employee_collection.delete_one({"_id": id})

    async def get_all(self, params):
        employee_list = []
        cursor = self.employee_collection.find({"name": {'$regex': params['search_query'], '$options': 'i'}} if params["search_query"] != "" else {}).sort(
            params["order_by"], params["order_direction"]).skip(params["skip"]).limit(params["size"])
        async for document in cursor:
            document["country"]= document["country"]["name"]
            document["province"]= document["province"]["name"]
            response_data = EmployeeReuestPayload(**document)
            response_data.id = str(document["_id"])
            del document["_id"]
            employee_list.append(response_data)

        total_count = await self.employee_collection.aggregate([
            {
                "$count": "total_no"
            }
        ]).to_list(None)
        if len(total_count) == 0:
            total_document = {"total_no": 0}
        else:
            total_document = total_count[0]

        return employee_list, total_document


    async def update_by_id(self, object_id_valid, payload: EmployeeResponse):
        update_request_payload = jsonable_encoder(
            payload)
        del update_request_payload["id"]
        # To keep old values of these fields during update operation; delete from payload
        del update_request_payload["createdAt"]
        del update_request_payload["createdByEmail"]
        del update_request_payload["createdByExternalId"]
            
        response = await self.employee_collection.update_one({"_id": object_id_valid}, {"$set": update_request_payload})
        return response
    

    async def get_field_detail(self, employee_id, field_value: str):
        filter = {"clientId": str(employee_id), field_value: {"$exists": True}}
        slip_documents = await self.employee_log_collection.aggregate([
            {
                "$match": filter
            },
            { 
                "$sort" : {"date": -1}
            },
            {
                "$project": {
                    "_id": 0,
                    "userId": "$userId",
                    "userEmail": "$userEmail",
                    "clientId": "$clientId",
                    "employeeId": "$employeeId",
                    field_value: f"${field_value}"        
                }
            }
        ]).to_list(None)
        return slip_documents
    

    async def get_ddl(self, client_id: str):
        response_ddl =await self.employee_collection.aggregate([
            {
                "$match":{
                    "clientId": str(client_id),
                    },
        },
        {
                 "$project":{
                    "_id": 0,
                    "label": {"$concat":["$firstName"," ","$lastName"]},
                    "value": {"$toString": "$_id"}
                 }}   
                ]).to_list(None)
        return response_ddl