from typing import Annotated

from fastapi import Depends, FastAPI
from sqlmodel import Session
from starlette.middleware.cors import CORSMiddleware

from .auth import get_current_user, router as auth_router
from .database import create_db_and_tables, get_session
from .models import User, UserRead
from .routers import posts


app = FastAPI()




app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




@app.on_event("startup")
def on_startup():
    create_db_and_tables()



app.include_router(posts.router)

app.include_router(auth_router)


@app.get(
    "/users/me",
    response_model=UserRead,
)
def read_me(
    current_user: Annotated[
        User,
        Depends(get_current_user)
    ],
):
    return current_user