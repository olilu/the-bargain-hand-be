from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
import http

from pydantic_models.wishlist import WishlistShow, WishlistCreate, WishlistUpdate
from data_adapter.wishlist import list_wishlists, create_new_wishlist, update_wishlist
from data_adapter.session import get_db

api_router = APIRouter(tags=["wishlist"],prefix="/wishlist")

@api_router.get("/all",status_code=http.HTTPStatus.OK,response_model=List[WishlistShow])
def return_all_wishlists(db:Session=Depends(get_db)):
    wishlists = list_wishlists(db)
    return wishlists

@api_router.post("/create",status_code=http.HTTPStatus.OK,response_model=WishlistCreate)
def create_wishlist(wishlist:WishlistCreate, db:Session=Depends(get_db)):
    wishlist = create_new_wishlist(wishlist,db)
    return wishlist

@api_router.post("/update",status_code=http.HTTPStatus.OK,response_model=WishlistUpdate)
def update_wishlist(wishlist:WishlistUpdate, db:Session=Depends(get_db)):
    wishlist = update_wishlist(wishlist,db)
    return wishlist
