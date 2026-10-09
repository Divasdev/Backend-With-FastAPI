from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings,SettingsConfigDict

APP_DIR=Path(__file__).resolve().parent #the backend/App folder

class Settings(BaseSettings):
   model_config=SettingsConfigDict(
      env_file=APP_DIR.parent / ".env", #backend/.env
      env_file_encoding="utf-8",
   )

   secret_key:SecretStr
   algorithm:str="HS256"
   access_token_expire_minutes:int=30
   database_url:str=f"sqlite:///{APP_DIR / 'database.db'}"
   cors_origins:list[str]=["http://localhost:5173"]
   

   upload_dir:Path=APP_DIR/"uploads"

   upload_dir.mkdir(exist_ok=True)

settings=Settings() #type: ignore[call-arg] #Loaded from .env  file
