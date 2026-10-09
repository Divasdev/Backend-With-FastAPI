from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Annotated
from uuid import uuid4

import jwt
from fastapi import APIRouter, Depends, File, Form, HTTPException, status,UploadFile
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from sqlmodel import Session, select
from .config import settings
from .database import get_session
from .models import Token, User, UserCreate, UserRead


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)

password_hash = PasswordHash.recommended()

SECRET_KEY = settings.secret_key.get_secret_value()
ALGORITHM = settings.algorithm




def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    return password_hash.verify(
        plain_password,
        hashed_password,
    )


def hash_password(password: str) -> str:
    return password_hash.hash(password)



def create_access_token(
    data: dict,
    expires_delta: timedelta | None = None,
) -> str:

    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    return encoded_jwt




@router.post(
    "/login",
    response_model=Token,
)
def login(
    form_data: Annotated[
        OAuth2PasswordRequestForm,
        Depends()
    ],
    session: Session = Depends(get_session),
):

    email = form_data.username.lower()

    user = session.exec(
        select(User).where(User.email == email)
    ).first()

    if not user or not verify_password(
        form_data.password,
        user.hashed_password,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    access_token = create_access_token(
        data={
            "sub": str(user.id)
        },
        expires_delta=timedelta(
            minutes=settings.access_token_expire_minutes
        ),
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
def register_user(

    email: Annotated[str, Form()],
    password: Annotated[str, Form(min_length=8)],
    profile_image: Annotated[UploadFile | None, File()] = None,
    session: Session = Depends(get_session),
):

    email = email.lower()

    existing = session.exec(
        select(User).where(User.email == email)
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    image_file=None
    
    if profile_image is not None and profile_image.filename:
        
        suffix=Path(profile_image.filename).suffix.lower() # type: ignore
        
        image_file=f"{uuid4().hex}{suffix}"
        
        upload_path=settings.upload_dir/image_file
        
        contents =profile_image.file.read()
        
        with upload_path.open("wb") as destination:
            destination.write(contents)
            
    
    user = User(
        email=email,
        hashed_password=hash_password(
            password
        ), 
        image_file=image_file,
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    return user




def get_current_user(
    token: Annotated[
        str,
        Depends(oauth2_scheme)
    ],
    session: Session = Depends(get_session),
) -> User:

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={
            "WWW-Authenticate": "Bearer"
        },
    )

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        user_id = payload.get("sub")

        if user_id is None:
            raise credentials_exception

    except (InvalidTokenError, ValueError):
        raise credentials_exception

    user = session.get(
        User,
        int(user_id),
    )

    if user is None:
        raise credentials_exception

    return user