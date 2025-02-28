import asyncio

from bson.objectid import ObjectId
from fastapi.encoders import jsonable_encoder
from motor.motor_asyncio import AsyncIOMotorClient

from app.config.config import DATABASE_NAME, MONGODB_CON_STR
from app.models.common.ddl_entity import DDLEntity
from app.models.master_data.client_model import ClientResponse, ClientReuestPayload


class ClientDatabase():
    client = AsyncIOMotorClient(MONGODB_CON_STR)
    client.get_io_loop = asyncio.get_running_loop
    client_collection = client[DATABASE_NAME]["client"]
    client_log_collection = client[DATABASE_NAME]["client_log"]

    async def create(self, document: ClientResponse):
        document = jsonable_encoder(document)
        del document["id"]
        # Removed update fields during the add operation
        del document["updatedAt"]
        del document["updatedByEmail"]
        del document["updatedByExternalId"]
        result = await self.client_collection.insert_one(document)
        document["id"] = result.inserted_id
        return document
    
    async def create_client_log(self, document: dict):
        result = await self.client_log_collection.insert_one(document)
        return document

    async def get_by_where_clause(self, where_clause: dict):
        return await self.client_collection.find_one(where_clause)

    async def get_by_id(self, id: ObjectId):
        return await self.client_collection.find_one({"_id": id})

    async def delete_by_id(self, id: ObjectId):
        return await self.client_collection.delete_one({"_id": id})
    

    async def get_all(self, accountant_id: str, params):
        filter = {"accountantId": str(accountant_id)}
        if len(params["search_query"]) > 0:
            filter = {
                "accountantId": str(accountant_id),
                "$or": [
                    {"name": {'$regex': params['search_query'], '$options': 'i'}},
                    {"accountNo": {'$regex': params['search_query'], '$options': 'i'}}
                ]
            }
        cursor_data = await self.client_collection.aggregate([
            {
                "$match": filter
            },
            {
                "$facet": {
                    "totalCount": [
                        {"$count": "count"}
                    ],
                    "data": [
                        {
                            "$sort": {
                                params["order_by"]: params["order_direction"]
                            }
                        },
                        {
                            "$skip": params['skip']
                        },
                        {
                            "$limit": params["size"]
                        },
                        {
                            "$project": {
                                "_id": 0,
                                "id": {"$toString": "$_id"},
                                "legalName": "$legalName",
                                "operatingName": "$operatingName",
                                "craBussinessNo": "$craBussinessNo",
                                "city": "$address.city.name",
                                "systemAlertsFrom": "$address.systemAlertsFrom",
                                "stubAlertsFrom": "$stubAlertsFrom",
                                "phone": "$address.phone",
                            }
                        }
                    ]
                }
            }
        ], collation={"locale": "en", "strength": 2}).to_list(None)

        total_count = cursor_data[0]["totalCount"][0]["count"] if cursor_data[0]["totalCount"] else 0
        data = cursor_data[0]["data"]

        return {"total_count": total_count, "data": data }


    async def update_by_id(self, object_id_valid, payload: ClientResponse):
        update_request_payload = jsonable_encoder(
            payload)
        del update_request_payload["id"]
        # To keep old values of these fields during update operation; delete from payload
        # del update_request_payload["createdAt"]
        # del update_request_payload["createdByEmail"]
        # del update_request_payload["createdByExternalId"]
            
        response = await self.client_collection.update_one({"_id": object_id_valid}, {"$set": update_request_payload})
        return response
    

    async def get_field_detail(self, client_id, field_value: str):
        filter = {"clientId": str(client_id), field_value: {"$exists": True}}
        slip_documents = await self.client_log_collection.aggregate([
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
                    field_value: f"${field_value}"        
                }
            }
        ]).to_list(None)
        return slip_documents
    


    async def get_ddl(self, accountant_id:str):
        response_ddl =await self.client_collection.aggregate([
            {
                "$match":{
                    "accountantId": str(accountant_id),
                    },
        },
        {
                 "$project":{
                    "_id": 0,
                    "label": "$legalName",
                    "value": {"$toString": "$_id"}
                 }}   
                ]).to_list(None)
        return response_ddl