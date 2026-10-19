from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session, select
from starlette.middleware.cors import CORSMiddleware

from .auth import get_current_user, router as auth_router
from .config import settings
from .database import get_session
from .models import User, UserRead, Vote, VoteRead
from .routers import posts

app = FastAPI()



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


@app.get("/users/me", response_model=UserRead)
def read_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user


@app.get("/users/me/votes", response_model=list[VoteRead])
def read_votes(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Session = Depends(get_session),
):
    return session.exec(select(Vote).where(Vote.user_id == current_user.id)).all()


@app.get("/users/{user_id}", response_model=UserRead)
def get_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user