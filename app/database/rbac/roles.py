import asyncio
from bson import ObjectId
from app.config.config import DATABASE_NAME, MONGODB_CON_STR
from fastapi.encoders import jsonable_encoder
from motor.motor_asyncio import AsyncIOMotorClient
from app.models.rbac.data_roles import UserRolesRequestModel, UserRolesResponseModel


class RolesDatabase():
    client = AsyncIOMotorClient(MONGODB_CON_STR)
    client.get_io_loop = asyncio.get_running_loop
    roles_collection = client[DATABASE_NAME]["roles"]


    async def create_role(self, payload: UserRolesRequestModel):
        document = jsonable_encoder(payload)
        result = await self.roles_collection.insert_one(document)
        document["id"] = str(result.inserted_id)
        del document["_id"]
        return document
    
    def get_by_whereclouse(self, where_clouse):
        return self.roles_collection.find_one(where_clouse)
    
    async def delete_by_id(self, id: ObjectId):
        return await self.roles_collection.delete_one({"_id": id})

    async def update_by_id(self, id: ObjectId, payload: UserRolesRequestModel):
        update_request_payload = jsonable_encoder(
            payload)
        result = await self.roles_collection.update_one({"_id": id}, {"$set": update_request_payload})
        return result

    async def get_all(self, params):
        taxslip_categories = []
        cursor = self.roles_collection.find({"roleName": {'$regex': params['search_query'], '$options': 'i'}} if params["search_query"] != "" else {}).sort(
            params["order_by"], params["order_direction"]).skip(params["skip"]).limit(params["size"])
        async for document in cursor:
            response_data = UserRolesResponseModel(**document)
            response_data.id = document["_id"]
            del document["_id"]
            taxslip_categories.append(response_data)

        total_count = await self.roles_collection.aggregate([
            {
                "$count": "total_no"
            }
        ]).to_list(None)
        if len(total_count) == 0:
            total_document = {"total_no": 0}
        else:
            total_document = total_count[0]

        return taxslip_categories, total_document