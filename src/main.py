from datetime import datetime, timedelta
from typing import Annotated
from config.env import Settings
from jose import JWTError, jwt
from passlib.context import CryptContext
from redis_om.model import NotFoundError
from db.config import redis_db as redis
import uvicorn
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from db.models import TokenData, User, UserRead, UserCreate, UserUpdate, Token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*'],
)


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, Settings().secret_key, algorithms=[Settings().algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = User.find(User.username == token_data.username).first()
    if user is None:
        raise credentials_exception
    return user


@app.get("/", response_model=UserRead, dependencies=[Depends(oauth2_scheme)], status_code=status.HTTP_200_OK)
async def get_user(user: Annotated[User, Depends(get_current_user)]) -> UserRead:
    return user


@app.get("/rating", response_model=list[UserRead], status_code=status.HTTP_200_OK)
async def get_users_rating(limit: int = 50, offset: int = 0) -> list[UserRead]:
    return [User.get(pk) for pk in redis.zrange(Settings().sorted_set_key, start=offset, end=limit+offset-1, desc=True)]


@app.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(new_user: UserCreate) -> UserRead:
    new_user.password = pwd_context.hash(new_user.password)
    user = User(**new_user.dict())
    redis.zadd(Settings().sorted_set_key, {user.pk:user.max_score}, nx=True)
    return user.save()


@app.put("/", response_model=UserRead, dependencies=[Depends(oauth2_scheme)], status_code=status.HTTP_202_ACCEPTED)
async def update_user(user_new: UserUpdate, user: Annotated[User, Depends(get_current_user)]) -> UserRead:
    if not user_new.max_score is None:
        if user_new.max_score < user.max_score:
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f"New socre must be higher: Given score {user_new.max_score} is lower than original score {user.max_score}")
        user.max_score = user_new.max_score
        user.score_date = datetime.now()
        redis.zadd(Settings().sorted_set_key, {user.pk:user.max_score}, xx=True, gt=True)
    if user_new.password:
        user.password = pwd_context.hash(user_new.password)
    if user_new.username:
        user.username = user_new.username
    if user_new.skin_id:
        user.skin_id = user_new.skin_id
    user.update()
    return user



def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, Settings().secret_key, algorithm=Settings().algorithm)
    return encoded_jwt


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(username: str, password: str):
    try:
        user: User = User.find(User.username == username).first()
        if not verify_password(password, user.password):
            return False
        else:
            return user
    except NotFoundError:
        return False



@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user: User = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=Settings().access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


if __name__ == '__main__':
    uvicorn.run("main:app", port=8222, reload=True, host="127.0.0.1")
