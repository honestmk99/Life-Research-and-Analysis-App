import os

# ----------------- Database variables (MongoDB) --------------------------

# --------------- Storage/Volume variables, must match the location set in docker-compose.yml -----------------------
from pathlib import Path

from starlette.datastructures import CommaSeparatedStrings
STATIC_PATH = Path(os.path.join(os.path.dirname(__file__), "app/static/"))
CURRENT_STATIC = Path('/static')
IMAGE_PATH = Path('/image-storage')
CACHE_PATH = Path('/cache-storage')
# CACHE_PATH = Path(os.path.join(os.path.dirname(__file__), "app/static/cache-storage"))

ALLOWED_HOSTS = CommaSeparatedStrings(os.getenv("ALLOWED_HOSTS", ""))

MONGODB_URL = os.getenv("MONGODB_URL", "")  # deploying without docker-compose
if not MONGODB_URL:
    MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
    MONGO_PORT = int(os.getenv("MONGO_PORT", 27017))
    MONGO_USER = os.getenv("MONGO_USER", "user")
    MONGO_PASS = os.getenv("MONGO_PASSWORD", "pass")
    

    if os.getenv("IS_PRODUCTION") and os.getenv("IS_PRODUCTION") == 'true':
        MONGO_DB_NAME = os.getenv("MONGO_DB", "db")
    elif os.getenv("IS_TESTING") and os.getenv("IS_TESTING") == 'true':
        MONGO_DB_NAME = os.getenv("MONGO_DB", "test_db")
    else:
        MONGO_DB_NAME = os.getenv("MONGO_DB", "dev_db")

    MONGODB_URL = f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}:{MONGO_PORT}"
    # MONGODB_URL = f"mongodb://localhost:{MONGO_PORT}"

#
# class BasicSettings(BaseSettings):
#     mongo_url: str = Field(..., env='MONGODB_URL')
#     mongo_db_name: str = 'db'
#     image_path: Path = Path('/image-storage')
#     cache_path: Path = Path('/cache-storage')
#
#
# class DevSettings(BasicSettings):
#     mongo_db_name: str = 'devDB'
#
#
# class TestSettings(BasicSettings):
#     mongo_db_name: str = 'testDB'


# @functools.lru_cache
# def get_settings() -> BasicSettings:
#     if os.environ.get("IS_PRODUCTION", 'false').lower() == 'true':
#         return BasicSettings()
#     elif os.environ.get("IS_TESTING", 'false').lower() == 'true':
#         return TestSettings()
#     else:
#         return DevSettings()
#

# # @functools.lru_cache
# def get_db() -> AsyncIOMotorDatabase:
#     settings = get_settings()
#
#     client = AsyncIOMotorClient(settings.mongo_url)
#     db: AsyncIOMotorDatabase = client[settings.mongo_db_name]
#
#     return db

