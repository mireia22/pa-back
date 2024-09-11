from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta
from db.models.user import User
from db.config import userCollection
from db.schemas.user import user_schema
import os

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={404: {"message": "Not found"}}
)

# JWT and password hashing configuration
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")

crypt = CryptContext(schemes=["bcrypt"], deprecated="auto")  # Password hashing config
oauth2 = OAuth2PasswordBearer(tokenUrl="login")  # For token-based auth


# Helper function to search user in the DB
def search_user(username: str):
    user = userCollection.find_one({"username": username})
    if user:
        # Ensure user dict includes '_id' and other fields
        return User(
            id=str(user["_id"]),  # Convert ObjectId to string
            username=user["username"],
            image=user.get("image", "/default.png"),  # Provide default if not present
            attractions_want=user.get("attractions_want", []),
            attractions_gone=user.get("attractions_gone", []),
            password=user["password"]
        )
    return None


# Authenticate user by verifying JWT token
async def authenticate_user(token: str = Depends(oauth2)):
    exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        username = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]).get("sub")
        if username is None:
            raise exception
    except JWTError:
        raise exception

    user = search_user(username)
    if user is None:
        raise exception

    return user


# Register route: Hash password before storing
@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(user: User):
    existing_user = userCollection.find_one({"username": user.username})
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")

    hashed_password = crypt.hash(user.password)
    user_dict = user.dict()
    user_dict["password"] = hashed_password

    result = userCollection.insert_one(user_dict)
    new_user = userCollection.find_one({"_id": result.inserted_id})
    return User(
        id=str(new_user["_id"]),  # Ensure id is included
        username=new_user["username"],
        image=new_user.get("image", "/default.png"),
        attractions_want=new_user.get("attractions_want", []),
        attractions_gone=new_user.get("attractions_gone", []),
        password=new_user["password"]
    )


@router.post("/login")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    user_db = userCollection.find_one({"username": form.username})
    if not user_db:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect username or password")

    if not crypt.verify(form.password, user_db["password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")

    access_token = {
        "sub": form.username,
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    encoded_jwt = jwt.encode(access_token, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": encoded_jwt, "token_type": "bearer"}


# Protected route: Only accessible by authenticated users
@router.get("/me")
async def read_users_me(current_user: User = Depends(authenticate_user)):
    return current_user
