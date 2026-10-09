from typing import Annotated
from fastapi import FastAPI,Form
from pathlib import Path 
from fastapi.responses import FileResponse


app=FastAPI()
BASE_DIR=Path(__file__).resolve().parent

@app.get("/")

def home():
    return FileResponse(BASE_DIR/"index.html")

@app.post("/register/")
async def register(
    username:Annotated[str,Form()],email:Annotated[str,Form()],password:Annotated[str,Form()]
):
    
    
    
    return {
        "username":username,
        "email":email
          }
    
    
    
