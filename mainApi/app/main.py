from fastapi import (
    FastAPI, APIRouter,
    Request,
    Response
)
from typing import Callable

from starlette.middleware.cors import CORSMiddleware
from starlette.middleware import Middleware

import os
from mainApi.app.auth.routers import router as auth_router
from mainApi.app.db.mongodb_utils import connect_to_mongo, close_mongo_connection
from mainApi.app.images.routers import router as image_router
from mainApi.config import ALLOWED_HOSTS
from fastapi.staticfiles import StaticFiles 
from fastapi.responses import JSONResponse, FileResponse
from fastapi.routing import APIRoute
from mainApi.config import STATIC_PATH
# from mainApi.config import connect_db, close_db
# from mainApi.app.images.utils import file
# import logging
# from fastapi.logger import logger as fastapi_logger


# gunicorn_error_logger = logging.getLogger("gunicorn.error")
# gunicorn_logger = logging.getLogger("gunicorn")
# uvicorn_access_logger = logging.getLogger("uvicorn.access")
# uvicorn_access_logger.handlers = gunicorn_error_logger.handlers
# fastapi_logger.handlers = gunicorn_error_logger.handlers
# fastapi_logger.setLevel(logging.DEBUG)

middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_methods=['*'],
        allow_headers=['*']
    )
]
app = FastAPI(title='IAS Project', middleware=middleware)

# app = FastAPI(title='IAS Project')
# origins = ['*']
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=['*'],
#     allow_headers=['*']
# )

script_dir = os.path.dirname(__file__)
st_abs_file_path = os.path.join(script_dir, "static/")


def get_value():
    global st_abs_file_path
    return st_abs_file_path


app.mount("/static", StaticFiles(directory=st_abs_file_path), name="static")

if not ALLOWED_HOSTS:
    ALLOWED_HOSTS = ["*"]


app.add_event_handler("startup", connect_to_mongo)
app.add_event_handler("shutdown", close_mongo_connection)

# ================= Routers  ===============
app.include_router(auth_router)
app.include_router(image_router)

test_router = APIRouter(
    prefix="/test",
    tags=["test"]
)


@test_router.get("", response_description="Test endpoint, will return the request")
async def _test(request: str = None):
    if request:
        return request
    else:
        return "Pass any string as 'request' query parameter and it will return it. ex. /test/?request=foo"


@app.get("/")
def read_root():
    return {"Ping": "Pong"}


app.include_router(test_router)
#
# # ================ Authentication Middleware =======================
# #----------- Here authentication is based on basic scheme,
# #----------- another authentication, based on bearer scheme, is used throughout
# #---------- the application (as decribed in FastAPI official documentation)
# @app.middleware("http")
# async def authenticate(request: Request, call_next):
#
# #-------------------- Authentication basic scheme -----------------------------
#     if "Authorization" in request.headers:
#         auth = request.headers["Authorization"]
#         try:
#             scheme, credentials = auth.split()
#             if scheme.lower() == 'basic':
#                 decoded = base64.b64decode(credentials).decode("ascii")
#                 username, _, password = decoded.partition(":")
#                 request.state.user = await authenticate_user(username, password)
#         except (ValueError, UnicodeDecodeError, binascii.Error):
#             raise HTTPException(
#                 status_code=status.HTTP_401_UND,
#                 detail="Invalid basic auth credentials"
#             )
#
#     response = await call_next(request)
#     return response
