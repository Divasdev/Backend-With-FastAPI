from typing import Annotated
from fastapi import FastAPI,Form
from pathlib import Path 
from fastapi.responses import FileResponse
from pwdlib import PasswordHash
from pydantic import BaseModel



app=FastAPI()


BASE_DIR=Path(__file__).resolve().parent

password_hash = PasswordHash.recommended()
class FormData(BaseModel):
    username:str 
    email:str
    password:str

class FormReturn(BaseModel):
    username:str
    email:str
    

@app.get("/")

def home():
    return FileResponse(BASE_DIR/"index.html")


@app.post("/register/")
async def register(data:Annotated[FormData,Form()]):
    
    hashed_password = password_hash.hash(data.password)
    return FormReturn(
        username=data.username,
        email=data.email
    )
    
    
    
