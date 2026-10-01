from fastapi import FastAPI,Depends,HTTPException,status
from starlette.middleware.cors import CORSMiddleware
from .routers import posts
from .database import create_db_and_tables

from pwdlib import PasswordHash
from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError

from .config import settings


oauth2_scheme=OAuth2PasswordBearer(tokenUrl="token")

password_hash=PasswordHash.recommended()


app=FastAPI()

SECRET_KEY=settings.secret_key
ALGORITHM=settings.algorithm


    


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # your React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
   create_db_and_tables()
   
app.include_router(posts.router)


def verify_password(plain_password,hashed_password):
    return password_hash.verify(plain_password,hashed_password)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


