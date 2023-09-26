import logging
from fastapi import FastAPI
from config.settings import settings
from data_adapter.session import engine
from data_adapter.db_models.base import Base
from controller.wishlist_controller import api_router as wishlist_controller
from controller.wishlist_games_controller import api_router as wishlist_games_controller
from controller.search_controller import api_router as search_controller
from controller.price_check_controller import api_router as price_check_controller

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%d/%m/%Y %H:%M:%S')

def create_tables():
    Base.metadata.create_all(bind=engine)

def start_application():
    create_tables()
    app = FastAPI(title=settings.PROJECT_TITLE, verstion=settings.PROJECT_VERSION)
    app.include_router(wishlist_controller)
    app.include_router(wishlist_games_controller)
    app.include_router(search_controller)
    app.include_router(price_check_controller)
    return app


app = start_application()

@app.on_event("startup")
async def startup_event():
    logging.warn("Startup Event Triggered")

@app.on_event("shutdown")
async def shutdown_event():
    logging.warn("Shutdown Event Triggered")

