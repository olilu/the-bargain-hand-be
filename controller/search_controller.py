from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import http

from pydantic_models.wishlist_game import WishlistGameFull
from pydantic_models.wishlist import WishlistUpdate
from service.search_service import SearchService

api_router = APIRouter(tags=["search"], prefix="/search")

@api_router.post("/game", status_code=http.HTTPStatus.OK, response_model=List[WishlistGameFull], summary="Search for a whishlist game in a shop")
def search_game(wishlist: WishlistUpdate, query: str, shop: str):
    if not wishlist or wishlist == {}:
        raise HTTPException(status_code=http.HTTPStatus.BAD_REQUEST,
                            detail=f"wishlist must not be empty")
    if shop not in ["PlayStation", "Nintendo"]:
        raise HTTPException(status_code=http.HTTPStatus.BAD_REQUEST,
                            detail=f"shop {shop} is not supported")
    if query == "":
        raise HTTPException(status_code=http.HTTPStatus.BAD_REQUEST,
                            detail=f"query must not be empty")

    search_service = SearchService(
        wishlist_uuid=wishlist.uuid,
        country_code=wishlist.country_code,
        language_code=wishlist.language_code
    )
    games = search_service.search(query=query, shop=shop)
    return games