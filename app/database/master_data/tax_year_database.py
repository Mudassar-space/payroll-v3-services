import asyncio
from bson import ObjectId
from app.config.config import DATABASE_NAME, MONGODB_CON_STR
from fastapi.encoders import jsonable_encoder
from motor.motor_asyncio import AsyncIOMotorClient
from app.models.master_data.country import CountryResponsePayload
from app.models.master_data.tax_year import TaxYearListModel, TaxYearRequestPayload, TaxYearResponsePayload


class TaxYearDatabase():
    client = AsyncIOMotorClient(MONGODB_CON_STR)
    client.get_io_loop = asyncio.get_running_loop
    tax_year_collection = client[DATABASE_NAME]["taxYear"]


    async def create(self, payload: TaxYearRequestPayload):
        document = jsonable_encoder(payload)
        del document["id"]
        del document["updatedAt"]
        del document["updatedByEmail"]
        del document["updatedByExternalId"]
        result = await self.tax_year_collection.insert_one(document)
        document["id"] = str(result.inserted_id)
        del document["_id"]
        return document
    
    def get_by_where_clause(self, where_clouse):
        return self.tax_year_collection.find_one(where_clouse)
    
    async def delete_by_id(self, id: ObjectId):
        return await self.tax_year_collection.delete_one({"_id": id})

    async def update_by_id(self, id: ObjectId, payload: TaxYearResponsePayload):
        update_request_payload = jsonable_encoder(
            payload)
        del update_request_payload["id"]
        del update_request_payload["createdAt"]
        del update_request_payload["createdByEmail"]
        del update_request_payload["createdByExternalId"]
        result = await self.tax_year_collection.update_one({"_id": id}, {"$set": update_request_payload})
        return result

    async def get_all(self, params):
        total_count_data = []
        cursor = self.tax_year_collection.find({"taxYear": {'$regex': params['search_query'], '$options': 'i'}} if params["search_query"] != "" else {}).sort(
            params["order_by"], params["order_direction"]).skip(params["skip"]).limit(params["size"])
        async for document in cursor:
            response_data = TaxYearListModel(**document)
            response_data.id = str(document["_id"])
            del document["_id"]
            total_count_data.append(response_data)

        total_count = await self.tax_year_collection.aggregate([
            {
                "$count": "total_no"
            }
        ]).to_list(None)
        if len(total_count) == 0:
            total_document = {"total_no": 0}
        else:
            total_document = total_count[0]

        return total_count_data, total_document
    

    async def get_ddl(self):
        response_ddl =await self.tax_year_collection.aggregate([       
        {
                 "$project":{
                    "_id": 0,
                    "label": "$taxYear",
                    "value": {"$toString": "$_id"},
                 }}   
                ]).to_list(None)
        return response_ddl
    