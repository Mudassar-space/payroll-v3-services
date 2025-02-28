import asyncio
from uuid import UUID

from app.config.config import DATABASE_NAME, MONGODB_CON_STR
from fastapi.encoders import jsonable_encoder
from motor.motor_asyncio import AsyncIOMotorClient

from app.models.rbac.user_authentication import Register


class OAuthDatabase():
    client = AsyncIOMotorClient(MONGODB_CON_STR)
    client.get_io_loop = asyncio.get_running_loop
    oauth_collection = client[DATABASE_NAME]["oauth"]
    
    async def updated_user_detail(self, payload: dict):
        document = jsonable_encoder(payload)
        await self.oauth_collection.update_one({"email":document["email"]}, {"$set": document})
        # await self.oauth_collection.update_one({"$set": document})
        return document
    
    def get_by_whereclouse(self, where_clouse):
        data = self.oauth_collection.find_one(where_clouse)
        return data
    
    async def login(self, payload: Register):
        document = jsonable_encoder(payload)
        await self.oauth_collection.insert_one(document)
        return document
    
    def get_by_whereclouse_data(where_clouse):
        data = OAuthDatabase.oauth_collection.find_one(where_clouse)
        return data