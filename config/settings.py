import os
from dotenv import load_dotenv

from pathlib import Path
env_path = Path('.')/'dev.env'
load_dotenv(dotenv_path=env_path)

class Settings:
    PROJECT_TITLE: str = "Bargain Hand"
    PROJECT_VERSION: str = "0.1.0"

    POSTGRES_USER: str = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD : str = os.getenv("POSTGRES_PASSWORD")    
    POSTGRES_SERVER : str = os.getenv("POSTGRES_SERVER")    
    POSTGRES_PORT : int = os.getenv("POSTGRES_PORT")
    POSTGRES_DB : str = os.getenv("POSTGRES_DB")
    DATABASE_URL: str = f"postgresql+psycopg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"

print(Settings().DATABASE_URL)
settings = Settings()