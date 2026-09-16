from fastapi import FastAPI,Depends,Query,Request,Body
from fastapi import Depends, FastAPI, Query,Request,Body
from  pydantic import  BaseModel,Field
from fastapi import HTTPException
from typing import Annotated
from sqlmodel import Field,Session,SQLModel,create_engine,select 
from datetime import date
from starlette.middleware.cors import CORSMiddleware
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

@app.post("/api/snippets/",response_model=SnipPublic)

def create_snip(snip:SnipCreate,session:SessionDep):
   db_snip=Snip.model_validate(snip)
   session.add(db_snip)
   session.commit()
   session.refresh(db_snip)
   return db_snip


@app.get("/api/snippets/",response_model=list[SnipPublic])
def read_heroes(
   session:SessionDep,
   offset:int=0,
   limit:Annotated[int,Query(le=100)]=100,
   ):
   
   snipps=session.exec(
      select(Snip)
      .offset(offset)
      .limit(limit) 
   ).all()
   
   return snipps 

@app.get("/api/snippets/{id}",response_model=SnipPublic)
def  read_hero(
   id:int,
   session:SessionDep
):
   snip=session.get(Snip,id)
   if not snip:
      raise HTTPException(status_code=404,detail="Snip not Found")
   
   return snip


@app.patch("/api/snippets/{id}",response_model=SnipPublic)
def update_snip(id:int,session:SessionDep,snip:SnipUpdate):
   snip_db=session.get(Snip,id)
   if not snip_db:
      raise HTTPException(status_code=404,detail="Snippet not found")
   snip_data=snip.model_dump(exclude_unset=True)
   snip_db.sqlmodel_update(snip_data)
   session.add(snip_db)
   session.commit()
   session.refresh(snip_db)
   return snip_db
   
   
@app.delete("/api/snippets/{id}")
def delete_hero(id:int,session:SessionDep):
   snip=session.get(Snip,id)
   if not snip:
      raise HTTPException(status_code=404,detail="Snippet not found")
   session.delete(snip)
   session.commit()
   
   return {"ok":True}