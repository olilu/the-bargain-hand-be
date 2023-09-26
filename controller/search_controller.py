from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
import http

from pydantic_models.wishlist_game import WishlistGameFull
from service.search_service import SearchService
from data_adapter.wishlist import get_wishlist_by_uuid
from data_adapter.session import get_db

api_router = APIRouter(tags=["search"], prefix="/search")

@api_router.get("/game", status_code=http.HTTPStatus.OK, response_model=List[WishlistGameFull], summary="Search for a whishlist game in a shop")
def search_game(wishlist_uuid: str, query: str, shop: str, db: Session = Depends(get_db)):
    if not wishlist_uuid:
        raise HTTPException(status_code=http.HTTPStatus.BAD_REQUEST,
                            detail=f"wishlist must not be empty")
    wishlist = get_wishlist_by_uuid(wishlist_uuid, db)
    if shop not in ["PlayStation", "Nintendo"]:
        raise HTTPException(status_code=http.HTTPStatus.BAD_REQUEST,
                            detail=f"shop {shop} is not supported")
    if query == "":
        raise HTTPException(status_code=http.HTTPStatus.BAD_REQUEST,
                            detail=f"query must not be empty")

    search_service = SearchService(
        wishlist=wishlist
    )
    games = search_service.search(query=query, shop=shop)
    return games