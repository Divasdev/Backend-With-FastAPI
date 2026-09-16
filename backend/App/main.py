from fastapi import FastAPI,Depends,Query,Request,Body
from fastapi import Depends, FastAPI, Query,Request,Body
from fastapi.responses import PlainTextResponse,JSONResponse
from  pydantic import  BaseModel,Field
from fastapi import HTTPException
from starlette.exceptions import HTTPException as starletteHTTPException 
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from typing import Annotated
from sqlmodel import Field,Session,SQLModel,create_engine,select 

from datetime import date

sqlite_file_name="database.db"
sqlite_url=f"sqlite:///{sqlite_file_name}"

engine=create_engine(sqlite_url,connect_args={"check_same_thread":False})


class SnipBase(SQLModel):
   title:str
   language:str 
   code:str 
   description:str 
   
class Snip(SnipBase,table=True):
   id:int|None=Field(default=None,primary_key=True)
   created_at:date=Field(default_factory=date.today)
   
class SnipCreate(SnipBase):
   pass 
class SnipPublic(SnipBase):
    id: int
    created_at: date
   
   
   
def create_db_and_tables():
   SQLModel.metadata.create_all(engine)
      

def get_session():
   with Session(engine) as session:
      yield session
      
SessionDep=Annotated[Session,Depends(get_session)]

app=FastAPI()

@app.on_event("startup")
def on_startup():
   create_db_and_tables()

@app.post("/snippets/",response_model=SnipPublic)

def create_snip(snip:SnipCreate,session:SessionDep):
   db_snip=Snip.model_validate(snip)
   session.add(db_snip)
   session.commit()
   session.refresh(db_snip)
   return db_snip