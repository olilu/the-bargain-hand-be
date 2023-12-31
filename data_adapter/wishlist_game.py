from sqlalchemy.orm import Session
from sqlalchemy import select
import uuid

from data_adapter.db_models.wishlist_game import WishlistGame
from data_adapter.db_models.game import Game
from data_adapter.game import delete_game_by_id
from pydantic_models.wishlist_game import WishlistGameFull

def link_game_to_wishlist(wishlist_game: WishlistGame, db: Session,):
    wishlist_game_model = wishlist_game.model_dump()
    wishlist_game_model["uuid"] = str(uuid.uuid4())
    wishlist_game_entry = WishlistGame(**wishlist_game_model)
    db.add(wishlist_game_entry)
    db.commit()
    db.refresh(wishlist_game_entry)
    return wishlist_game_entry

def unlink_game_from_wishlist(wishlist_uuid: str, game_id: str, db: Session):
    wishlist_game_entry = db.query(WishlistGame).filter(WishlistGame.wishlist_uuid == wishlist_uuid, WishlistGame.game_id == game_id).first()
    if wishlist_game_entry is None:
        return False
    db.delete(wishlist_game_entry)
    db.commit()
    return True

def get_wishlist_game_by_uuid(wishlist_game_uuid: str, db: Session,):
    return db.query(WishlistGame).filter(WishlistGame.uuid == wishlist_game_uuid).first()

def update_wishlist_game_by_uuid(wishlist_game_uuid: str, wishlist_game: WishlistGame, db: Session):
    wishlist_game_model = wishlist_game.model_dump()
    wishlist_game_model["uuid"] = wishlist_game_uuid
    existing_wishlist_game = db.query(WishlistGame).filter(WishlistGame.uuid == wishlist_game_uuid)
    if existing_wishlist_game.first() is None:
        return False
    existing_wishlist_game.update(wishlist_game_model)
    db.commit()
    return True

def get_wishlist_games_by_wishlist_uuid(wishlist_uuid:str, db:Session):
    select_query = select(WishlistGame,Game).join(Game, WishlistGame.game_id == Game.id, isouter=True).filter(WishlistGame.wishlist_uuid == wishlist_uuid)
    result = db.execute(select_query).all()
    wishlist_games = []
    for row in result:
        wishlist_game = row[0]
        game = row[1]
        wishlist_games.append(
            WishlistGameFull(
                uuid=wishlist_game.uuid,
                wishlist_uuid=wishlist_game.wishlist_uuid,
                game_id=wishlist_game.game_id,
                price_new=wishlist_game.price_new,
                price_old=wishlist_game.price_old,
                currency=wishlist_game.currency,
                on_sale=wishlist_game.on_sale,
                name=game.name,
                shop=game.shop,
                img_link=game.img_link,
                link=game.link,
            )
        )
    return wishlist_games

def delete_wishlist_games_by_wishlist_uuid(wishlist_uuid:str, db:Session):
    games_in_wishlist = db.query(WishlistGame).filter(WishlistGame.wishlist_uuid == wishlist_uuid).all()
    games = []
    for game_link in games_in_wishlist:
        games.append(game_link.game_id)
        db.delete(game_link)
        db.commit()
    for game_id in games:
        remaining_links = get_wishlist_links_by_game_id(game_id, db)
        if remaining_links == []:
            delete_game_by_id(game_id, db)
    return True

def get_wishlist_links_by_game_id(game_id:str, db:Session):
    return db.query(WishlistGame).filter(WishlistGame.game_id == game_id).all()


