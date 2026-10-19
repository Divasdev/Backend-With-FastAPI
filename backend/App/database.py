from typing import Annotated
from fastapi import Depends
from sqlmodel import Session,SQLModel,create_engine

from .config import settings

url=settings.database_url
connect_args={"check_same_thread":False} if url.startswith("sqlite") else{}

engine=create_engine(
   url,
   connect_args=connect_args,
   pool_pre_ping=True,
)


      

def get_session():
   with Session(engine) as session:
      yield session
      
SessionDep=Annotated[Session,Depends(get_session)]
