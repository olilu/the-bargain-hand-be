import logging
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware

from config.settings import settings
from data_adapter.session import engine, SessionLocal
from data_adapter.db_models.base import Base
from controller.wishlist_controller import api_router as wishlist_controller
from controller.wishlist_games_controller import api_router as wishlist_games_controller
from controller.search_controller import api_router as search_controller
from controller.price_check_controller import api_router as price_check_controller
from service.utilities.tasks import repeat_every
from service.price_check_service import run_price_checks_all_wishlists

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%d/%m/%Y %H:%M:%S')
origins = [
    "http://localhost:3000",
    "http://localhost:5173"
]

def create_tables():
    Base.metadata.create_all(bind=engine)

def start_application():
    create_tables()
    app = FastAPI(title=settings.PROJECT_TITLE, verstion=settings.PROJECT_VERSION)
    app.include_router(wishlist_controller)
    app.include_router(wishlist_games_controller)
    app.include_router(search_controller)
    app.include_router(price_check_controller)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
)
    return app


app = start_application()

@app.on_event("startup")
async def startup_event():
    logging.warning("Startup Event Triggered")

@app.on_event("startup")
@repeat_every(seconds=60*60*12)
def schedule_price_checks():
    logging.warning("Start scheduled price checks")
    background_tasks = BackgroundTasks()
    background_tasks.add_task(run_price_checks_all_wishlists(db=SessionLocal()))

@app.on_event("shutdown")
async def shutdown_event():
    logging.warning("Shutdown Event Triggered")

