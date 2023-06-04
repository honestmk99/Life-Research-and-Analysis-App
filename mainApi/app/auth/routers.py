import pyotp
from bson import ObjectId

from fastapi import (
    APIRouter,
    Depends,
    status,
    HTTPException, Form
)
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import ReturnDocument
from pymongo.results import InsertOneResult

from .auth import (
    get_current_user,
    authenticate_user,
    create_access_token,
    get_password_hash, get_current_admin_user, create_user, login, login_swagger, update_user_password,
    update_current_user, get_user_by_email, authenticate_email_password
)

# from .settings import ACCESS_TOKEN_EXPIRE_MINUTES, db
from .settings import ACCESS_TOKEN_EXPIRE_MINUTES

from typing import List
from datetime import datetime, timedelta

from mainApi.app.auth.models.user import UserModelDB, ShowUserModel, UpdateUserModel, CreateUserModel, \
    CreateUserReplyModel, LoginUserReplyModel, ChangeUserPasswordModel, UpdateUserAdminModel, to_camel
from mainApi.app.db.mongodb import get_database
from mysql.connector import connect, Error

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)


# ============= Creating path operations ==============
@router.post("/register",
             response_description="Add new user",
             response_model=CreateUserReplyModel,
             status_code=status.HTTP_201_CREATED)
async def register(user: CreateUserModel, db: AsyncIOMotorDatabase = Depends(get_database)) -> CreateUserReplyModel:
    print("Here is token cheking process!")
    return await create_user(user, db)


@router.post("/token", response_model=LoginUserReplyModel)
async def _login_swagger(form_data: OAuth2PasswordRequestForm = Depends(),
                         db: AsyncIOMotorDatabase = Depends(get_database)) -> LoginUserReplyModel:
    """
        Login route, returns Bearer Token.
        SWAGGER FRIENDLY.
        Due to the swagger Api not letting me add otp as a required parameter
        the otp needs to be added to the the end of the password
        ex. 'passwordotpotp' .. no space just right after and otp is always 6 digits

        TODO find way to modify swagger to let me add otp separately, no login2 needed
    """
    return await login_swagger(form_data=form_data, db=db)


@router.post("/login", response_model=LoginUserReplyModel)
async def _login(form_data: OAuth2PasswordRequestForm = Depends(),
                 otp: str = Form(...),
                 db: AsyncIOMotorDatabase = Depends(get_database)) -> LoginUserReplyModel:
    """
    Login route, returns Bearer Token.
    NOT SWAGGER FRIENDLY.
    Separate otp and OAuth2PasswordRequestForm.
    Prettier than the /token function since the requirement of otp is made clear
    """

    return await login(form_data=form_data, otp=otp, db=db)


@router.post("/auth_email_password", status_code=status.HTTP_200_OK, response_description="Authenticate Email and Password")
async def _auth_email_password(form_data: OAuth2PasswordRequestForm = Depends(),
                               db: AsyncIOMotorDatabase = Depends(get_database)):
    """
    First step in 2 Factor Auth, user_name and password only.
    Returns either HTTP_200_OK or HTTP_401_UNAUTHORIZED, depending on the email and password given.

    This does not log the user in, no token is given.
    They must still call the /login endpoint with email, password and otp to login.
    This just allows the front end to verify that the email and password is good and that they can
    go ahead and show the OTP form.

    Notice that the front end still needs to keep the email and password to be reset in the full /login
    with the otp.
    """

    # username is email
    user: UserModelDB = await get_user_by_email(form_data.username, db)
    is_user_auth = authenticate_email_password(
        user, password=form_data.password)
    if not is_user_auth:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect Authentication Data",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get("/current", response_description="Current User", response_model=ShowUserModel)
async def current_user(current_user: UserModelDB = Depends(get_current_user)):
    # we do not return the full UserModel, only the ShowUserModel
    return ShowUserModel.parse_obj(current_user.dict())


@router.get("/renew_token",
            response_description=f"Renews token for another {ACCESS_TOKEN_EXPIRE_MINUTES} minutes",
            response_model=LoginUserReplyModel)
async def renew_token(current_user: UserModelDB = Depends(get_current_user)) -> LoginUserReplyModel:
    # create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(user_id=str(
        current_user.id), expires_delta=access_token_expires)

    reply = LoginUserReplyModel(
        user=ShowUserModel.parse_obj(current_user),
        access_token=access_token,
        token_type="Bearer"
    )

    return reply


@router.put("/update_current_user", response_description="Update Current User", response_model=ShowUserModel)
async def _update_current_user(update_data: UpdateUserModel,
                               current_user: UserModelDB = Depends(
                                   get_current_user),
                               db: AsyncIOMotorDatabase = Depends(get_database)):
    result: UserModelDB = await update_current_user(update_data, current_user, db)

    return ShowUserModel.parse_obj(jsonable_encoder(result))


@router.put("/change_password", response_description="Change User Password", response_model=ShowUserModel)
async def _change_password(data: ChangeUserPasswordModel,
                           current_user: UserModelDB = Depends(
                               get_current_user),
                           db: AsyncIOMotorDatabase = Depends(get_database)):
    user: UserModelDB = await update_user_password(old_password=data.old_password,
                                                   otp=data.otp,
                                                   new_password=data.new_password,
                                                   db=db,
                                                   current_user=current_user)

    return ShowUserModel.parse_obj(jsonable_encoder(user))


#  ---------- ADMIN ----------

@router.get("/admin/list", response_description="List all users", response_model=List[ShowUserModel])
async def list_users(max_entries: int = None,
                     admin_user: UserModelDB = Depends(get_current_admin_user),
                     db: AsyncIOMotorDatabase = Depends(get_database)):
    if max_entries is None:
        max_entries = 1000

    users = await db["users"].find().to_list(max_entries)
    users = [ShowUserModel.parse_obj(user) for user in users]

    return users


@router.get("/purchase", response_description="List purchase", response_model=List[str])
async def list_purchase(max_entries: int = None,
                     current_user: UserModelDB = Depends(get_current_user),
                     db: AsyncIOMotorDatabase = Depends(get_database)):
    if max_entries is None:
        max_entries = 1000

    purchase_info = []
    try:
        with connect(
            host="localhost",
            user="wordpress",
            password="JbeT67wU5ArydL",
            database="wordpress",
        ) as connection:
            print(connection)
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM customer_purchases")
                result = cursor.fetchall()
                for row in result:
                    print(row)
                    purchase_info.append(row)
    except Error as e:
        print(e)
        return JSONResponse({"success": False, "error": ""})

    return JSONResponse({"success": True, "data": purchase_info})


@router.put("/admin/{user_id}", response_description="Update a user", response_model=ShowUserModel)
async def update_user(user_id: str,
                      update_data: UpdateUserAdminModel,
                      admin_user: UserModelDB = Depends(
                          get_current_admin_user),
                      db: AsyncIOMotorDatabase = Depends(get_database)) -> ShowUserModel:
    # we must filter out the non set optional items in the update data
    # the key is also converted into lowerCamelCase
    update_data = {to_camel(k): v for (k, v) in update_data.dict(
    ).items() if k in update_data.__fields_set__}

    if len(update_data) < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Not update data")

    result: UserModelDB = await db["users"].find_one_and_update(
        {'_id': ObjectId(user_id)},
        {"$set": update_data},
        return_document=ReturnDocument.AFTER
    )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"User {user_id} not found")
    else:
        return ShowUserModel.parse_obj(result)


@router.delete("/admin/{user_id}", response_description="Delete a user")
async def delete_user(user_id: str,
                      admin_user: UserModelDB = Depends(
                          get_current_admin_user),
                      db: AsyncIOMotorDatabase = Depends(get_database)):
    delete_result = await db["users"].delete_one({"_id": user_id})

    if delete_result.deleted_count == 1:
        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404, detail=f"User {user_id} not found")
