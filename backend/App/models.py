from sqlmodel import SQLModel,Field

from datetime import date 


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
   
   