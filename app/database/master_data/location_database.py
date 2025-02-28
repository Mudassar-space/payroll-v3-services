import asyncio
from bson import ObjectId
from app.config.config import DATABASE_NAME, MONGODB_CON_STR
from fastapi.encoders import jsonable_encoder
from motor.motor_asyncio import AsyncIOMotorClient

from app.models.common.ddl_entity import DDLEntity
from app.models.master_data.location import LocationResponsePayload
from app.models.master_data.team import TeamResponsePayload


class LocationDatabase():
    client = AsyncIOMotorClient(MONGODB_CON_STR)
    client.get_io_loop = asyncio.get_running_loop
    location_collection = client[DATABASE_NAME]["locations"]


    async def create(self, payload: LocationResponsePayload):
        document = jsonable_encoder(payload)
        del document["id"]
        del document["updatedAt"]
        del document["updatedByEmail"]
        del document["updatedByExternalId"]
        result = await self.location_collection.insert_one(document)
        document["id"] = str(result.inserted_id)
        del document["_id"]
        return document
    
    def get_by_whereclause(self, where_clause):
        return self.location_collection.find_one(where_clause)
    
    async def delete_by_id(self, id: ObjectId):
        return await self.location_collection.delete_one({"_id": id})

    async def update_by_id(self, id: ObjectId, payload: LocationResponsePayload):
        update_request_payload = jsonable_encoder(
            payload)
        # del update_request_payload["id"]
        # del update_request_payload["createdAt"]
        # del update_request_payload["createdByEmail"]
        # del update_request_payload["createdByExternalId"]
        result = await self.location_collection.update_one({"_id": id}, {"$set": update_request_payload})
        return result

    async def get_all(self, client_id: str, params):
        location_list = []
        filter = {"clientId": str(client_id)}
        if len(params["search_query"]) > 0:
            filter = {
                "locationName": {'$regex': params['search_query'],  '$options': 'i'},
                "clientId": str(client_id)
            }
        cursor = self.location_collection.find(filter, {"locationName": 1, "notes": 1}).sort(
            params["order_by"], params["order_direction"]).skip(params["skip"]).limit(params["size"])
        async for document in cursor:
            document["id"] = str(document["_id"])
            del document["_id"]
            location_list.append(document)
            
        total_count =await self.location_collection.aggregate([{
                "$match": {"clientId": str(client_id)}},
                {
                "$count": "total_no"
                }
                ]).to_list(None)
        if  len(total_count) == 0:
            total_document = {"total_no": 0}
        else: 
            total_document = total_count[0]
       
        return location_list, total_document

    async def get_ddl(self, client_id:str):
        location_ddl =await self.location_collection.aggregate([
            {
                "$match":{
                    "clientId":client_id,
                    },
        },
        {
                 "$project":{
                    "_id": 0,
                    "label": "$locationName",
                    "value": {"$toString": "$_id"}
                 }}   
                ]).to_list(None)
        return location_ddl
    