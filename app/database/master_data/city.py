import asyncio
from bson import ObjectId
from app.config.config import DATABASE_NAME, MONGODB_CON_STR
from fastapi.encoders import jsonable_encoder
from motor.motor_asyncio import AsyncIOMotorClient
from app.models.master_data.city import CityDdlResponsePayload, CityRequestPayload, CityResponsePayload
from app.models.master_data.country import CountryRequestPayload, CountryResponsePayload


class CityDatabase():
    client = AsyncIOMotorClient(MONGODB_CON_STR)
    client.get_io_loop = asyncio.get_running_loop
    city_collection = client[DATABASE_NAME]["city"]


    async def create(self, payload: CityRequestPayload):
        document = jsonable_encoder(payload)
        result = await self.city_collection.insert_one(document)
        document["id"] = str(result.inserted_id)
        del document["_id"]
        return document
    
    def get_by_whereclouse(self, where_clouse):
        return self.city_collection.find_one(where_clouse)
    
    async def delete_by_id(self, id: ObjectId):
        return await self.city_collection.delete_one({"_id": id})

    async def update_by_id(self, id: ObjectId, payload: CityResponsePayload):
        update_request_payload = jsonable_encoder(
            payload)
        result = await self.city_collection.update_one({"_id": id}, {"$set": update_request_payload})
        return result

    async def get_all(self, params):
        total_count_data = []
        cursor = self.city_collection.find({"name": {'$regex': params['search_query'], '$options': 'i'}} if params["search_query"] != "" else {}).sort(
            params["order_by"], params["order_direction"]).skip(params["skip"]).limit(params["size"])
        async for document in cursor:
            response_data = CityResponsePayload(**document)
            response_data.id = document["_id"]
            del document["_id"]
            total_count_data.append(response_data)

        total_count = await self.city_collection.aggregate([
            {
                "$count": "total_no"
            }
        ]).to_list(None)
        if len(total_count) == 0:
            total_document = {"total_no": 0}
        else:
            total_document = total_count[0]

        return total_count_data, total_document
    
    
    async def get_ddl(self, client_id:str):
        response_ddl =await self.city_collection.aggregate([
            
        {
                 "$project":{
                     "_id": 0,
                    "label": "$name",
                    "value": {"$toString": "$_id"},
                    "shortCode": "$shortCode"
                 }}   
                ]).to_list(None)
        return response_ddl

