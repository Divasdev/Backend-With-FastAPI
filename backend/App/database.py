from pathlib import Path
from typing import Annotated
from fastapi import Depends
from sqlmodel import Session,SQLModel,create_engine

sqlite_file_path = Path(__file__).resolve().parent / "database.db"
sqlite_url = f"sqlite:///{sqlite_file_path}"

engine=create_engine(sqlite_url,connect_args={"check_same_thread":False})


   
def create_db_and_tables():
   SQLModel.metadata.create_all(engine)
      

def get_session():
   with Session(engine) as session:
      yield session
      
SessionDep=Annotated[Session,Depends(get_session)]
