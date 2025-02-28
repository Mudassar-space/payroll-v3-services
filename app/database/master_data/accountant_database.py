import asyncio

from bson.objectid import ObjectId
from fastapi.encoders import jsonable_encoder
from app.models.common.ddl_entity import DDLEntity
from app.models.master_data.accountant import AccountantListModel, AccountantResponse
from motor.motor_asyncio import AsyncIOMotorClient

from app.config.config import DATABASE_NAME, MONGODB_CON_STR


class AccountantDatabase():
    client = AsyncIOMotorClient(MONGODB_CON_STR)
    client.get_io_loop = asyncio.get_running_loop
    accountant_collection = client[DATABASE_NAME]["accountant"]
    accountant_log_collection = client[DATABASE_NAME]["accountant_log"]


    async def create(self, document: AccountantResponse):
        document = jsonable_encoder(document)
        del document["id"]
        del document["updatedAt"]
        del document["updatedByEmail"]
        del document["updatedByExternalId"]
        result = await self.accountant_collection.insert_one(document)
        document["id"] = result.inserted_id
        return document
    
    async def create_accountant_log(self, document: dict):
        result = await self.accountant_log_collection.insert_one(document)
        return document

    async def get_by_where_clause(self, where_clause: dict):
        return await self.accountant_collection.find_one(where_clause)

    async def get_by_id(self, id: ObjectId):
        return await self.accountant_collection.find_one({"_id": id})

    async def delete_by_id(self, id: ObjectId):
        return await self.accountant_collection.delete_one({"_id": id})


    async def get_all(self, params):
        filter = {}
        if len(params["search_query"]) > 0:
            filter = {
                "$or": [
                    {"firstName": {'$regex': params['search_query'], '$options': 'i'}},
                    {"lastName": {'$regex': params['search_query'], '$options': 'i'}},
                    {"accTitle": {'$regex': params['search_query'], '$options': 'i'}}
                ]
            }
        cursor_data = await self.accountant_collection.aggregate([
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
                                "name": {"$concat": ["$firstName", " ", "$lastName"]},
                                "accTitle": "$accTitle",
                                "email": "$address.email",
                                "phone": "$address.phone",
                                "city": "$address.city.name"
                            }
                        }
                    ]
                }
            }
        ], collation={"locale": "en", "strength": 2}).to_list(None)

        total_count = cursor_data[0]["totalCount"][0]["count"] if cursor_data[0]["totalCount"] else 0
        data = cursor_data[0]["data"]

        return {"total_count": total_count, "data": data }


    async def update_by_id(self, object_id_valid, payload: AccountantResponse):
        update_request_payload = jsonable_encoder(
            payload)
        del update_request_payload["id"]
        del update_request_payload["createdAt"]
        del update_request_payload["createdByEmail"]
        del update_request_payload["createdByExternalId"]
        response = await self.accountant_collection.update_one({"_id": object_id_valid}, {"$set": update_request_payload})
        return response
    

    async def get_field_detail(self, accountant_id, field_value: str):
        filter = {"accountId": str(accountant_id), field_value: {"$exists": True}}
        slip_documents = await self.accountant_log_collection.aggregate([
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
                    "accountId": "$accountId",
                    field_value: f"${field_value}"        
                }
            }
        ]).to_list(None)
        return slip_documents
    

    async def get_ddl(self):
        response_ddl =await self.accountant_collection.aggregate([
        {
                 "$project":{
                     "_id": 0,
                    "label": "$accTitle",
                    "value": {"$toString": "$_id"}
                 }}   
                ]).to_list(None)
        return response_ddl
    