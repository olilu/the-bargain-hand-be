import logging
from fastapi import FastAPI
from config.settings import settings
from data_adapter.session import engine
from data_adapter.base import Base

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%d/%m/%Y %H:%M:%S')

def create_tables():
    Base.metadata.create_all(bind=engine)

def start_application():
    app = FastAPI(title=settings.PROJECT_TITLE, verstion=settings.PROJECT_VERSION)
    create_tables()
    return app


app = start_application()

@app.on_event("startup")
async def startup_event():
    logging.warn("Startup Event Triggered")

@app.on_event("shutdown")
async def shutdown_event():
    logging.warn("Shutdown Event Triggered")

