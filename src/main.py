import uvicorn
from fastapi import FastAPI, HTTPException, Response, status
from db.models import User, UserRead, UserCreate, UserUpdate
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.get("/", response_model=UserRead, status_code=status.HTTP_200_OK)
async def get_current_user():
    pass


@app.get("/", response_model=list[UserRead], status_code=status.HTTP_200_OK)
async def get_users_rating(limit: int = 50, skip: int = 0):
    pass


@app.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    pass


@app.put("/", response_model=UserRead, status_code=status.HTTP_202_ACCEPTED)
async def update_user(user: UserUpdate):
    pass


if __name__ == '__main__':
    uvicorn.run("main:app", port=8222, reload=True, host="127.0.0.1")
