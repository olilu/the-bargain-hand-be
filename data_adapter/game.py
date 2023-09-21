from sqlalchemy.orm import Session

from data_adapter.db_models.game import Game as Game_db_model
from pydantic_models.game import Game as Game_Pydantic


def create_game(game: Game_Pydantic, db: Session):
    game_entry = Game_db_model(**game.model_dump())
    db.add(game_entry)
    db.commit()
    db.refresh(game_entry)
    return game_entry


def get_game_by_id(id: str, db: Session):
    return db.query(Game_db_model).filter(Game_db_model.id == id).first()


def delete_game_by_id(id: str, db: Session):
    game_entry = db.query(Game_db_model).filter(Game_db_model.id == id).first()
    if game_entry is None:
        return False
    db.delete(game_entry)
    db.commit()
    return True
