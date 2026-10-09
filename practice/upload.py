from typing import Annotated
from fastapi import FastAPI,Form,File,UploadFile,HTTPException
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
    file:UploadFile
    
class FormReturn(BaseModel):
    username:str
    email:str
    url:str
    

@app.get("/")

def home():
    return FileResponse(BASE_DIR/"index.html")


    
@app.post("/register/",response_model=FormReturn)
async def register(
    username: Annotated[str, Form()],
    email: Annotated[str, Form()],
    password: Annotated[str, Form()],
    file: Annotated[UploadFile, File()],
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400,detail="only images are allowed,Bad Request")
    
    
    hashed_password = password_hash.hash(password)
    
    
    extension=Path(file.filename).suffix
    new_name=f"{uuid4().hex}{extension}"
    save_path=UPLOAD_DIR/new_name
    
    contents=await file.read()
    
    with open(save_path,'wb') as f:
        f.write(contents)
       
    
    return{"username":username,
       "email":email,
       "url":f"/uploads/{new_name}"
       }
    
    

    
