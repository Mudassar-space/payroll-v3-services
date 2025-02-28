import asyncio
from bson import ObjectId
from app.config.config import DATABASE_NAME, MONGODB_CON_STR
from fastapi.encoders import jsonable_encoder
from motor.motor_asyncio import AsyncIOMotorClient

from app.models.master_data.states import StatesDdlResponsePayload, StatesRequestPayload, StatesResponsePayload


class StatesDatabase():
    client = AsyncIOMotorClient(MONGODB_CON_STR)
    client.get_io_loop = asyncio.get_running_loop
    states_collection = client[DATABASE_NAME]["states"]


    async def create(self, payload: StatesRequestPayload):
        document = jsonable_encoder(payload)
        result = await self.states_collection.insert_one(document)
        document["id"] = str(result.inserted_id)
        del document["_id"]
        return document
    
    def get_by_whereclouse(self, where_clouse):
        return self.states_collection.find_one(where_clouse)
    
    async def delete_by_id(self, id: ObjectId):
        return await self.states_collection.delete_one({"_id": id})

    async def update_by_id(self, id: ObjectId, payload: StatesResponsePayload):
        update_request_payload = jsonable_encoder(
            payload)
        result = await self.states_collection.update_one({"_id": id}, {"$set": update_request_payload})
        return result

    async def get_all(self, params):
        total_count_data = []
        cursor = self.states_collection.find({"name": {'$regex': params['search_query'], '$options': 'i'}} if params["search_query"] != "" else {}).sort(
            params["order_by"], params["order_direction"]).skip(params["skip"]).limit(params["size"])
        async for document in cursor:
            response_data = StatesResponsePayload(**document)
            response_data.id = document["_id"]
            del document["_id"]
            total_count_data.append(response_data)

        total_count = await self.states_collection.aggregate([
            {
                "$count": "total_no"
            }
        ]).to_list(None)
        if len(total_count) == 0:
            total_document = {"total_no": 0}
        else:
            total_document = total_count[0]

        return total_count_data, total_document
    
    
    async def get_ddl(self, country_id:str):
        response_ddl =await self.states_collection.aggregate([
            {
                "$match":{
                    "countryId": str(country_id),
                    },
        },
        {
                 "$project":{
                    "_id": 0,
                    "label": "$name",
                    "value": {"$toString": "$_id"},
                    "shortCode": "$shortCode"
                 }}   
                ]).to_list(None)
        return response_ddl
    