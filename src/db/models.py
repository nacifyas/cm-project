from redis_om import HashModel, Field, Migrator
from fastapi import HTTPException, status
from db.config import redis_db as redis
from datetime import date, datetime
from pydantic import BaseModel, EmailStr, validator


class User(HashModel):
    email: EmailStr = Field(index=True)
    password: str
    name: str
    username: str = Field(index=True)
    skin_id: str
    birthdate: date
    max_score: int = 0
    score_date: datetime = datetime.now()

    class Meta:
        database = redis


class UserRead(BaseModel):
    pk: str
    email: EmailStr
    name: str
    username: str
    skin_id: str
    max_score: int = 0
    score_date: datetime = datetime.now()


class UserUpdate(BaseModel):
    password: str | None
    username: str | None
    skin_id: str | None
    max_score: int | None

    @validator("username")
    def validate_username_uniqueness(cls, value):
        if value:
            if (User.find(User.username == value).count()) > 0:
                raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f"Username {value} already taken")
        return value


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    username: str
    skin_id: str
    birthdate: date

    @validator("username")
    def validate_username_uniqueness(cls, value):
        if value:
            if (User.find(User.username == value).count()) > 0:
                raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f"Username {value} already taken")
        return value

    @validator("email")
    def validate_email_uniqueness(cls, value):
        if value:
            if (User.find(User.email == value).count()) > 0:
                raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f"Email {value} already exists")
        return value
    

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None

Migrator().run()
