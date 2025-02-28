import asyncio

from bson.objectid import ObjectId
from fastapi.encoders import jsonable_encoder
from app.models.common.ddl_entity import DDLEntity
from app.models.master_data.accountant import AccountantListModel, AccountantResponse, SingleAccountantModel
from motor.motor_asyncio import AsyncIOMotorClient

from app.config.config import DATABASE_NAME, MONGODB_CON_STR
from app.models.master_data.accountant_bank import AccountantBankResponse
from app.models.master_data.states import StatesDdlResponsePayload


class AccountantBankDatabase():
    client = AsyncIOMotorClient(MONGODB_CON_STR)
    client.get_io_loop = asyncio.get_running_loop
    accountant_bank_collection = client[DATABASE_NAME]["accountant_bank"]

    async def create(self, document: AccountantBankResponse):
        document = jsonable_encoder(document)
        del document["id"]
        # Removed update fields during the add operation
        del document["updatedAt"]
        del document["updatedByEmail"]
        del document["updatedByExternalId"]
        result = await self.accountant_bank_collection.insert_one(document)
        document["id"] = result.inserted_id
        return document

    async def get_by_where_clause(self, where_clause: dict):
        return await self.accountant_bank_collection.find_one(where_clause)

    async def get_by_id(self, id: ObjectId):
        return await self.accountant_bank_collection.find_one({"_id": id})

    async def delete_by_id(self, id: ObjectId):
        return await self.accountant_bank_collection.delete_one({"_id": id})

    
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
        cursor_data = await self.accountant_bank_collection.aggregate([
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
                                "name": "$name",
                                "primaryAccount": "$primaryAccount",
                                "status": "$status",
                                "accountNo": "$accountNo"
                            }
                        }
                    ]
                }
            }
        ], collation={"locale": "en", "strength": 2}).to_list(None)

        total_count = cursor_data[0]["totalCount"][0]["count"] if cursor_data[0]["totalCount"] else 0
        data = cursor_data[0]["data"]

        return {"total_count": total_count, "data": data }


    async def update_by_id(self, object_id_valid, payload: AccountantBankResponse):
        update_request_payload = jsonable_encoder(
            payload)
        del update_request_payload["id"]
        # To keep old values of these fields during update operation; delete from payload
        del update_request_payload["createdAt"]
        del update_request_payload["createdByEmail"]
        del update_request_payload["createdByExternalId"]
            
        response = await self.accountant_bank_collection.update_one({"_id": object_id_valid}, {"$set": update_request_payload})
        return response
    

    async def get_ddl(self, accountant_id:str):
        response_ddl =await self.accountant_bank_collection.aggregate([
            {
                "$match":{
                    "accountantId": str(accountant_id),
                    },
        },
        {
                 "$project":{
                     "_id": 0,
                    "label": "$name",
                    "value": {"$toString": "$_id"}
                 }}   
                ]).to_list(None)
        return response_ddl