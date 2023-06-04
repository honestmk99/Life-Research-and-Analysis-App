from bson import ObjectId
from fastapi import Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import ReturnDocument
from pymongo.results import InsertOneResult, UpdateResult

from .settings import pwd_context, oauth2_scheme, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
import pyotp

from datetime import datetime, timedelta
from typing import Optional

from mainApi.app.auth.models.user import UserModelDB, CreateUserModel, CreateUserReplyModel, ShowUserModel, \
    LoginUserReplyModel, UpdateUserModel, UpdateUserAdminModel, to_camel

from mainApi.app.db.mongodb import get_database
import qrcode
import qrcode.image.svg
# CRUD


async def create_user(user: CreateUserModel, db: AsyncIOMotorDatabase) -> CreateUserReplyModel:
    # check if another with the same email already exist
    existing_email = await db["users"].find_one({"email": user.email})
    if existing_email is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")

    # turn user into a dictionary so that we can add keys
    new_user_dict = user.dict()
    new_user_dict['created_at'] = datetime.now().strftime("%m/%d/%y %H:%M:%S")
    # last login same as created_at
    new_user_dict['last_login'] = new_user_dict['created_at']
    new_user_dict['hashed_password'] = get_password_hash(
        user.password)  # changing plain text password to hash
    otp_secret = pyotp.random_base32()  # generate secret to be shared with user
    new_user_dict['otp_secret'] = otp_secret
    new_user_dict['is_admin'] = True
    new_user_dict['_id'] = ObjectId()  # set specific unique id
    # turn new_user_dict into a UsermodelDB after adding created_at, changing password to hash and adding otp_secret
    # turning it into a UserModelDB so that we get validation
    new_user: UserModelDB = UserModelDB.parse_obj(new_user_dict)

    # must use jsonable_encoder
    insert_user_res: InsertOneResult = await db["users"].insert_one(new_user.dict(by_alias=True))
    if not insert_user_res.acknowledged:
        raise Exception(f"Failed to add User to Database, :{new_user}")

    created_user = ShowUserModel.parse_obj(new_user)

    otp_uri = pyotp.totp.TOTP(otp_secret).provisioning_uri(
        name=user.email, issuer_name='IAS App')

    otp_qr_svg = generate_qr_code_svg(otp_uri)

    # create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(user_id=str(
        new_user.id), expires_delta=access_token_expires)

    created_user_reply = CreateUserReplyModel(user=created_user,
                                              otp_secret=otp_secret,
                                              otp_uri=otp_uri,
                                              otp_qr_svg=jsonable_encoder(
                                                  otp_qr_svg),
                                              access_token=access_token,
                                              token_type="Bearer")

    return created_user_reply


def generate_qr_code_svg(data: str) -> str:
    svg = qrcode.make(data, image_factory=qrcode.image.svg.SvgPathImage)
    return svg.to_string()


async def get_current_user(db: AsyncIOMotorDatabase = Depends(get_database),
                           token: str = Depends(oauth2_scheme)) -> UserModelDB:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        used_id: str = payload.get("id")
        if used_id is None:
            raise credentials_exception
        # token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = await get_user_by_id(used_id, db)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: UserModelDB = Depends(get_current_user)) -> UserModelDB:
    if current_user.is_active:
        return current_user
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")


async def get_current_admin_user(current_user: UserModelDB = Depends(get_current_user)) -> UserModelDB:
    if current_user.is_admin:
        return current_user
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not admin")


async def update_current_user(update_data: UpdateUserModel,
                              current_user: UserModelDB,
                              db: AsyncIOMotorDatabase) -> UserModelDB:

    # we must filter out the non set optional items in the update data
    # the key is also converted into lowerCamelCase
    update_data = {to_camel(k): v for (k, v) in update_data.dict(
    ).items() if k in update_data.__fields_set__}

    result = await db["users"].find_one_and_update(
        {'_id': current_user.id},
        {"$set": update_data},
        return_document=ReturnDocument.AFTER
    )

    return UserModelDB.parse_obj(result)


async def update_user_password(old_password,
                               otp: str,
                               new_password: str,
                               db: AsyncIOMotorClient,
                               current_user: UserModelDB) -> UserModelDB:
    # check that the old password and otp is correct
    is_user_auth = authenticate_user(
        current_user, password=old_password, otp=otp)
    if not is_user_auth:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect Authentication Data",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # changing plain text password to hash
    new_password_hash = get_password_hash(new_password)

    updated_user = await db["users"].find_one_and_update(
        {'_id': current_user.id},
        {"$set": {'hashedPassword': new_password_hash}},
        return_document=ReturnDocument.AFTER
    )

    return UserModelDB.parse_obj(updated_user)


async def get_user_by_email(email: str, db: AsyncIOMotorClient) -> UserModelDB or None:
    user = await db["users"].find_one({"email": email})

    if user is not None:
        return UserModelDB.parse_obj(user)
    else:
        return None


async def get_user_by_id(user_id: str or ObjectId, db: AsyncIOMotorClient) -> UserModelDB or None:

    user = await db["users"].find_one({"_id": ObjectId(user_id)})

    if user is not None:
        return UserModelDB.parse_obj(user)
    else:
        return None


# END OF CRUD

async def login_swagger(form_data: OAuth2PasswordRequestForm, db: AsyncIOMotorClient, otp_code: str) -> LoginUserReplyModel:
    """
        Login route, returns Bearer Token.
        SWAGGER FRIENDLY.
        Due to the swagger Api not letting me add otp as a required parameter
        the otp needs to be added to the the end of the password
        ex. 'passwordotpotp' .. no space just right after and otp is always 6 digits

        TODO find way to modify swagger to let me add otp separately, no login2 needed
    """
    print(form_data.username, form_data.password)
    # password = form_data.password[:-6]  # exclude the last 6 digits
    # otp = form_data.password[-6:]  # include only the last 6 digits
    otp_code_len = len(otp_code)
    password = form_data.password[:-otp_code_len]  # exclude the last 6 digits
    print('password is ', password, ' otp is ', otp_code)
    # username is email
    user: UserModelDB = await get_user_by_email(form_data.username, db)
    is_user_auth = authenticate_user(user, password=password, otp_code=otp_code)
    if not is_user_auth:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect Authentication Data",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(user_id=str(
        user.id), expires_delta=access_token_expires)
    # update db with last_login time and set the user to is_active=True
    await db["users"].update_one({"email": form_data.username}, {"$set": {
        "lastLogin": datetime.now().strftime("%m/%d/%y %H:%M:%S"),
        "isActive": "true"
    }})

    reply = LoginUserReplyModel(
        user=ShowUserModel.parse_obj(user),
        access_token=access_token,
        token_type="Bearer"
    )
    return reply


async def login(form_data: OAuth2PasswordRequestForm, otp: str, db: AsyncIOMotorClient) -> LoginUserReplyModel:
    """
        Login route, returns Bearer Token.
        NOT SWAGGER FRIENDLY.
        Separate otp and OAuth2PasswordRequestForm.
        Prettier than the /token function since the requirement of otp is made clear
        """
    form_data.password += otp  # adds the otp to the end of the password to fit the login method
    return await login_swagger(form_data=form_data, db=db, otp_code=otp)


def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    # print("-----------------------------------------------");
    print('plain_password', plain_password)
    print('hashed_password', hashed_password)
    print('pwd_conte', pwd_context.verify(plain_password, hashed_password))
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_email_password(user: UserModelDB or None, password, otp_code) -> bool:
    # async def authenticate_user(form_data: OAuth2PasswordRequestForm = Depends()) -> UserModel or None:
    # user: UserModelDB = await get_user_by_email(email, db)
    print('password is ', password),
    if user is None:
        return False
    if otp_code != user.otp_secret:
        False
    if not verify_password(password, user.hashed_password):
        return False

    return True


def authenticate_user(user: UserModelDB or None, password, otp_code) -> bool:

    email_password_authenticated = authenticate_email_password(user, password, otp_code)
    return True
    if email_password_authenticated is False:
        return False

    # check the otp
    # totp = pyotp.TOTP(user.otp_secret)
    # if not totp.verify(otp):
    #     return False

    return True


def create_access_token(user_id: str, expires_delta: Optional[timedelta] = None) -> str:
    """ Create the token that the user will include in their header, claims must be json encodable """
    # to_encode = data.copy()
    claims = {"id": user_id}
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    claims.update({"exp": expire})
    encode_jwt = jwt.encode(claims=claims, key=SECRET_KEY, algorithm=ALGORITHM)
    return encode_jwt
