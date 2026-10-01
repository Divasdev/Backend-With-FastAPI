from fastapi import FastAPI,Depends,HTTPException,status
from sqlmodel import Session, select
from starlette.middleware.cors import CORSMiddleware
from .routers import posts
from .database import create_db_and_tables,get_session
from .models import User,UserCreate,UserRead,Token




from pwdlib import PasswordHash
from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError

from .config import settings


oauth2_scheme=OAuth2PasswordBearer(tokenUrl="/auth/login")

password_hash=PasswordHash.recommended()


app=FastAPI()

SECRET_KEY=settings.secret_key.get_secret_value()
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

def hash_password(password:str) ->str:
    return password_hash.hash(password)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@app.post("/auth/register",response_model=UserRead,status_code=status.HTTP_201_CREATED)

def register_user(user_in:UserCreate,session:Session=Depends(get_session)):
    email=user_in.email.lower()
    
    existing=session.exec(select(User).where(User.email==email)).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
        
    user=User(email=email,hashed_password=hash_password(user_in.password))
        
    session.add(user)
    session.commit()
    session.refresh(user)
    
    return user 


@app.post("/auth/login",response_model=Token)

def login(
    form_data:Annotated[OAuth2PasswordRequestForm,Depends()],
    session:Session=Depends(get_session),
    
):
    email=form_data.username.lower()
    
    
    user=session.exec(select(User).where(User.email==email)).first()
    
    
    if not user or not verify_password(
        form_data.password,
        user.hashed_password):
        
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect email or password",
        headers={"WWW-Authenticate":"Bearer"},
    )
        
        
    access_token=create_access_token(
        data={"sub":str(user.id)},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
    )
    
    return {"access_token":access_token,"token_type":"bearer"}


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Session = Depends(get_session),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # 1. Check the wristband: real signature? not expired?
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception

    # 2. Does this user still exist?
    user = session.get(User, int(user_id))
    if user is None:
        raise credentials_exception

    # 3. Hand the user to the route
    return user

         
@app.get("/users/me",response_model=UserRead)
def read_me(current_user:Annotated[User,Depends(get_current_user)]):
    return current_user

 
    

