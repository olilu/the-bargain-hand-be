from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
import http

from pydantic_models.wishlist_game import WishlistGameFull, WishlistGame
from service.price_check_service import PriceCheckService
from data_adapter.wishlist_game import get_wishlist_games_by_wishlist_uuid, update_wishlist_game_by_uuid
from data_adapter.wishlist import get_wishlist_by_uuid
from data_adapter.session import get_db

api_router = APIRouter(tags=["price check"], prefix="/wishlist")

@api_router.get("/{wishlist_uuid}/check-prices", status_code=http.HTTPStatus.OK, response_model=List[WishlistGameFull], summary="Check for bargains in your wishlist")
def check_for_bargains(wishlist_uuid: str, db: Session = Depends(get_db)):
    if not wishlist_uuid:
        raise HTTPException(status_code=http.HTTPStatus.BAD_REQUEST,
                            detail=f"wishlist must not be empty")
    wishlist = get_wishlist_by_uuid(wishlist_uuid, db)
    wishlist_games = get_wishlist_games_by_wishlist_uuid(wishlist_uuid, db)

    price_check_service = PriceCheckService(
        wishlist=wishlist,
        wishlist_games=wishlist_games
    )
    bargains = price_check_service.check_bargains(db=db)
    return bargains