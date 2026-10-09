from fastapi import FastAPI
from pathlib import Path

from fastapi.responses import FileResponse


app=FastAPI()
BASE_DIR=Path(__file__).resolve().parent

@app.get("/")

def home():
    return FileResponse(BASE_DIR/"index.html")




