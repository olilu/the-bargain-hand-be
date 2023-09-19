from fastapi import APIRouter

api_router = APIRouter()

@api_router.get("/")
def hello_world():
    return {"message": "Hello World!"}