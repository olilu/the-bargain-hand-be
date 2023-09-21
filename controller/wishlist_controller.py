from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import http

from pydantic_models.wishlist import WishlistShow, WishlistCreate
from pydantic_models.response import GenericResponse
from data_adapter.session import get_db
from data_adapter.wishlist import list_wishlists, get_wishlist_by_uuid, create_new_wishlist, update_wishlist as update_wishlist_db, delete_wishlist as delete_wishlist_db

api_router = APIRouter(tags=["wishlist management"],prefix="/wishlist")

# Wishlists management
@api_router.get("/all",status_code=http.HTTPStatus.OK,response_model=List[WishlistShow],summary="Get all wishlists")
def return_all_wishlists(db:Session=Depends(get_db)):
    wishlists = list_wishlists(db)
    return wishlists

@api_router.get("/{wishlist_uuid}",status_code=http.HTTPStatus.OK,response_model=WishlistShow,summary="Get a wishlist by uuid")
def return_wishlist_by_uuid(wishlist_uuid: str, db:Session=Depends(get_db)):
    wishlist = get_wishlist_by_uuid(wishlist_uuid,db)
    if wishlist is None:
        raise HTTPException(status_code=http.HTTPStatus.NOT_FOUND, detail=f"wishlist with uuid {wishlist_uuid} does not exist")
    return wishlist

@api_router.post("/create",status_code=http.HTTPStatus.OK,response_model=WishlistCreate, summary="Create a new wishlist")
def create_wishlist(wishlist:WishlistCreate, db:Session=Depends(get_db)):
    wishlist = create_new_wishlist(wishlist,db)
    return wishlist

@api_router.put("/update/{wishlist_uuid}",status_code=http.HTTPStatus.OK,response_model=GenericResponse, summary="Update a wishlist")
def update_wishlist(wishlist_uuid: str, wishlist:WishlistCreate, db:Session=Depends(get_db)):
    response = update_wishlist_db(wishlist_uuid,wishlist,db)
    if response is False:
        raise HTTPException(status_code=http.HTTPStatus.NOT_FOUND, detail=f"wishlist with uuid {wishlist_uuid} does not exist")
    return {"details": "wishlist successfully updated"}

@api_router.delete("/delete/{wishlist_uuid}",status_code=http.HTTPStatus.OK,response_model=GenericResponse,summary="Delete a wishlist")
def delete_wishlist(wishlist_uuid: str, db:Session=Depends(get_db)):
    response = delete_wishlist_db(wishlist_uuid, db)
    if response is False:
        raise HTTPException(status_code=http.HTTPStatus.NOT_FOUND, detail=f"wishlist with uuid {wishlist_uuid} does not exist")
    return {"details": "wishlist successfully deleted"}


