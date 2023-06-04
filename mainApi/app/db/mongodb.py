from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from mainApi.config import MONGO_DB_NAME


class DataBase:
    client: AsyncIOMotorClient = None


db = DataBase()


# async def get_database() -> AsyncIOMotorClient:
#     return db.client

async def get_database() -> AsyncIOMotorDatabase:
    return db.client[MONGO_DB_NAME]


async def get_database_client() -> AsyncIOMotorClient:
    return db.client
