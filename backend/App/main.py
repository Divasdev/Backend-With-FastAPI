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



sqlite_file_name="database.db"
sqlite_url=f"sqlite:///{sqlite_file_name}"

engine=create_engine(sqlite_url,connect_args={"check_same_thread":False})

