from aredis_om import HashModel, Field, Migrator
from db.config import redis_db
from datetime import date, datetime
from pydantic import BaseModel, EmailStr, validator
import asyncio


class User(HashModel):
    email: EmailStr
    encrypted_password: str
    name: str
    username: str = Field(index=True)
    skin_id: str
    birthdate: date
    max_score: int = 0
    score_date: datetime = datetime.now()

    class Meta:
        database = redis_db


class UserRead(BaseModel):
    pk: str
    email: EmailStr
    name: str
    username: str
    skin_id: str
    max_score: int = 0
    score_date: datetime = datetime.now()


class UserUpdate(BaseModel):
    pk: str
    password: str | None
    username: str | None
    skin_id: str | None
    max_score: int | None

    @validator("username")
    async def validate_username_uniqueness(cls, value):
        if value:
            if (await User.find(User.username == value).count()) > 0:
                raise ValueError(f"Username {value} already taken")
        return value
    
    @validator("max_score")
    async def validate_new_score(cls, value, values):
        if value:
            if await User.get(values["pk"]).max_score > value:
                raise ValueError(f"Username {value} already taken")
        return value 


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    username: str
    skin_id: str
    birthdate: date

    @validator("username")
    async def validate_username_uniqueness(cls, value):
        if value:
            if (await User.find(User.username == value).count()) > 0:
                raise ValueError(f"Username {value} already taken")
        return value
    

asyncio.run(Migrator().run())
