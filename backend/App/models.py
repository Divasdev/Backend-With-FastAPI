from sqlmodel import SQLModel,Field
from pydantic import field_validator

from datetime import date 


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

    @field_validator("title", "language", "code", "description")
    @classmethod
    def validate_supplied_fields(cls, value, info):
        # Omitted fields keep their defaults; explicitly supplied null is invalid.
        if value is None:
            raise ValueError("Must not be null; omit the field to leave it unchanged")
        if info.field_name != "description" and not value.strip():
            raise ValueError("Must not be blank")
        return value
