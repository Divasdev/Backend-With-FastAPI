from fastapi import FastAPI,Depends,Query,Request,Body
from fastapi import Depends, FastAPI, Query,Request,Body
from  pydantic import  BaseModel,Field
from fastapi import HTTPException
from typing import Annotated
from sqlmodel import Field,Session,SQLModel,create_engine,select 
from datetime import date
from starlette.middleware.cors import CORSMiddleware
from routers import posts 


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
   vote_count: int = Field(default=0) 
class SnipCreate(SnipBase):
   pass 
class SnipPublic(SnipBase):
    id: int
    created_at: date
    vote_count: int = Field(default=0) 

class SnipUpdate(SQLModel):
    title: str | None = None
    language: str | None = None
    code: str | None = None
    description: str | None = None
   
   
   
def create_db_and_tables():
   SQLModel.metadata.create_all(engine)
      

def get_session():
   with Session(engine) as session:
      yield session
      
SessionDep=Annotated[Session,Depends(get_session)]

app=FastAPI()


app.include_router(posts.router)



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

