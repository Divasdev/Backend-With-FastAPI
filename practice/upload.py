from typing import Annotated
from fastapi import FastAPI,Form,File,UploadFile
from pathlib import Path 
from fastapi.responses import FileResponse
from pwdlib import PasswordHash
from pydantic import BaseModel

from uuid import uuid4
from fastapi.staticfiles import StaticFiles

app=FastAPI()

BASE_DIR=Path(__file__).resolve().parent

UPLOAD_DIR=BASE_DIR/"uploads"

UPLOAD_DIR.mkdir(exist_ok=True)

print("Project directory:", BASE_DIR)
print("Uploads directory:", UPLOAD_DIR)

app.mount(
    "/uploads",
    StaticFiles(directory=UPLOAD_DIR),
    name="uploads"
)



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
async def register(data:Annotated[FormData,Form()],file:Annotated[UploadFile,File()]):
    
    hashed_password = password_hash.hash(data.password)
    
    print("uploaded filename:",file.filename)
    return{"username":data.username,
       "email":data.email,
       "filename":file.filename,
       "content-type":file.content_type
       }
    
    

    
