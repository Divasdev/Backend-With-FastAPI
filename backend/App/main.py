from fastapi import FastAPI,Depends,Query,Request,Body
from fastapi import Depends, FastAPI, Query,Request,Body
from  pydantic import  BaseModel,Field
from fastapi import HTTPException
from typing import Annotated
from sqlmodel import Field,Session,SQLModel,create_engine,select 
from datetime import date
from starlette.middleware.cors import CORSMiddleware
from routers import posts 

from database import create_db_and_tables



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
   
app.include_router(posts.router)

