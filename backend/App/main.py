from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI
from sqlmodel import Session
from starlette.middleware.cors import CORSMiddleware

from .auth import get_current_user, router as auth_router
from .config import settings
from .database import create_db_and_tables, get_session
from .models import User, UserRead,Vote
from .routers import posts
from fastapi.staticfiles import StaticFiles
from pathlib import Path
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs once when the server starts.
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)

app.mount(
    "/uploads",
    StaticFiles(directory=str(settings.upload_dir)),
    name="uploads",
    
)



app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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