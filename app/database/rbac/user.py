import asyncio
from uuid import UUID

from app.config.config import DATABASE_NAME, MONGODB_CON_STR
from fastapi.encoders import jsonable_encoder
from motor.motor_asyncio import AsyncIOMotorClient

from app.models.rbac.user_authentication import Register, UserRegistrationOut


class AuthenticationsDatabase():
    client = AsyncIOMotorClient(MONGODB_CON_STR)
    client.get_io_loop = asyncio.get_running_loop
    auth_user_collection = client[DATABASE_NAME]["auth_user"]


    async def register(self, payload: Register):
        document = jsonable_encoder(payload)
        await self.auth_user_collection.insert_one(document)
        return document
    
    async def updated_user_detail(self, payload: dict):
        await self.auth_user_collection.update_one({"email":payload["email"]}, {"$set": payload})
        return payload
    
    async def updated_user_password(self, where_clouse, payload: UserRegistrationOut):
        document = jsonable_encoder(payload)
        response = await self.auth_user_collection.update_one(where_clouse, {"$set": document})
        # await self.oauth_collection.update_one({"$set": document})
        return document
    
    def get_by_whereclouse(self, where_clouse):
        return self.auth_user_collection.find_one(where_clouse)
    
    