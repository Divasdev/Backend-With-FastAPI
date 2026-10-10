from typing import Literal
from sqlmodel import SQLModel,Field
from pydantic import BaseModel, field_validator

from datetime import datetime,timezone



class User(SQLModel,table=True):
    id:int|None=Field(default=None,primary_key=True)
    email:str|None=Field(unique=True,index=True)
    image_file:str|None=None
    hashed_password:str
    created_at: datetime=Field(default_factory=lambda : datetime.now(timezone.utc))
    @property
    def profile_image_url(self):
        if self.image_file:
            return f"/uploads/{self.image_file}"
        return None 
    
        
class UserCreate(SQLModel):
    email:str
    password:str=Field(min_length=8)
    
class UserRead(SQLModel):
    id:int
    email:str
    profile_image_url:str|None=None
    created_at:datetime

    
class Token(SQLModel):
    access_token:str
    token_type:str



class SnipBase(SQLModel):
   title:str
   language:str 
   code:str 
   description:str = ""
   

   @field_validator("title", "language", "code")
   @classmethod
   def reject_blank_content(cls, value):
      if not value.strip():
         raise ValueError("Must not be blank")
      return value
   
class Snip(SnipBase,table=True):
   id:int|None=Field(default=None,primary_key=True)
   owner_id: int = Field(foreign_key="user.id", index=True) 
   created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
   updated_at: datetime | None = None        
   vote_count: int = Field(default=0) 
   
class SnipCreate(SnipBase):
   pass 

class SnipPublic(SnipBase):
    id: int
    owner_id:int
    created_at: datetime=Field(default_factory=lambda : datetime.now(timezone.utc))
    vote_count: int = Field(default=0) 

class SnipUpdate(SQLModel):
    title: str | None = None
    language: str | None = None
    code: str | None = None
    description: str | None = None

    @field_validator("title", "language", "code", "description")
    @classmethod
    def validate_supplied_fields(cls, value, info):
        # Omitted fields keep their defaults; explicitly supplied null is invalid.
        if value is None:
            raise ValueError("Must not be null; omit the field to leave it unchanged")
        if info.field_name != "description" and not value.strip():
            raise ValueError("Must not be blank")
        return value

class Vote(SQLModel,table=True):
    user_id:int=Field(foreign_key="user.id",primary_key=True)
    snip_id:int=Field(foreign_key="snip.id",primary_key=True)
    value:int
    
class VoteIn(SQLModel):
    value:Literal[1,-1]
    
    