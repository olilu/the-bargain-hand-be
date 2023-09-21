from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import http

from pydantic_models.wishlist_game import WishlistGameFull, WishlistGame
from pydantic_models.game import Game
from pydantic_models.response import GenericResponse
from data_adapter.session import get_db
from data_adapter.wishlist_game import get_wishlist_games_by_wishlist_uuid, get_wishlist_links_by_game_id, link_game_to_wishlist, unlink_game_from_wishlist
from data_adapter.game import get_game_by_id, create_game, delete_game_by_id
from data_adapter.wishlist import get_wishlist_by_uuid

api_router = APIRouter(tags=["wishlist games management"], prefix="/wishlist")

# Whishlist Games management
@api_router.get("/{wishlist_uuid}/games",status_code=http.HTTPStatus.OK,response_model=List[WishlistGameFull],
                summary="Get all games in a wishlist")
def return_full_wishlist_games(wishlist_uuid: str, db:Session=Depends(get_db)):
    wishlist_games = get_wishlist_games_by_wishlist_uuid(wishlist_uuid,db)
    return wishlist_games

@api_router.post("/{wishlist_uuid}/add-game",status_code=http.HTTPStatus.OK,response_model=WishlistGame,
                summary="Add a game to a wishlist")
def add_game_to_wishlist(wishlist_uuid: str, wishlist_game: WishlistGameFull, db:Session=Depends(get_db)):
    if not get_wishlist_by_uuid(wishlist_uuid,db):
        raise HTTPException(status_code=http.HTTPStatus.NOT_FOUND, detail=f"wishlist with uuid {wishlist_uuid} does not exist")
    existing_links = get_wishlist_links_by_game_id(wishlist_game.game_id,db)
    for link in existing_links:
        if link.wishlist_uuid == wishlist_uuid:
            raise HTTPException(status_code=http.HTTPStatus.CONFLICT, detail=f"game with id {wishlist_game.game_id} already exists in wishlist with uuid {wishlist_uuid}")
    if not get_game_by_id(wishlist_game.game_id,db):
        game_entry = Game(
            id=wishlist_game.game_id,
            name=wishlist_game.name,
            shop=wishlist_game.shop,
            img_link=wishlist_game.img_link,
            link=wishlist_game.link,
        )
        create_game(game_entry,db)
    wishlist_link_entry = WishlistGame(
        wishlist_uuid=wishlist_uuid,
        game_id=wishlist_game.game_id,
        price_new=wishlist_game.price_new,
        price_old=wishlist_game.price_old,
    )
    wishlist_link_entry = link_game_to_wishlist(wishlist_link_entry,db)
    return wishlist_link_entry


@api_router.delete("/{wishlist_uuid}/remove-game/{game_id}",status_code=http.HTTPStatus.OK,response_model=GenericResponse,summary="Remove a game from a wishlist")
def remove_game_from_wishlist(wishlist_uuid: str, game_id: str, db:Session=Depends(get_db)):
    response = unlink_game_from_wishlist(wishlist_uuid,game_id,db)
    if response is False:
        raise HTTPException(status_code=http.HTTPStatus.NOT_FOUND, detail=f"game with id {game_id} does not exist in wishlist with uuid {wishlist_uuid}")
    remaining_links = get_wishlist_links_by_game_id(game_id,db)
    if len(remaining_links) == 0:
        response = delete_game_by_id(game_id,db)
        if response is False:
            raise HTTPException(status_code=http.HTTPStatus.NOT_FOUND, detail=f"game with id {game_id} does not exist")
    return {"details": "game successfully removed from wishlist"}