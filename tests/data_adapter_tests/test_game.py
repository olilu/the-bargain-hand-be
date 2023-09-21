from sqlalchemy.orm import Session
from datetime import datetime

from pydantic_models.game import Game
from data_adapter.game import create_game, get_game_by_id, delete_game_by_id

GAME = Game(
    id="EP9000-CUSA00470_00-JOURNEYPS4061115",
    name="Journey",
    shop="PlayStation",
    img_link="https://image.api.playstation.com/vulcan/img/rnd/202010/2917/Cj8ngIRc3MB1uhNR40BQhzXv.png?w=440&thumb=false",
    link="https://store.playstation.com/de-ch/product/EP9000-CUSA00470_00-JOURNEYPS4061115",
)

GAME2 = Game(
    id="EP2333-PPSA01826_00-PATHLESSSIEE0000",
    name="The Pathless",
    shop="PlayStation",
    img_link="https://image.api.playstation.com/vulcan/ap/rnd/202007/1500/PzzL4lymRdZuLEerjeL58HG8.png?w=440&thumb=false",
    link="https://store.playstation.com/de-ch/product/EP2333-PPSA01826_00-PATHLESSSIEE0000",
)

# Test the create_game function
def test_create_game(db_session:Session):
    result = create_game(GAME,db_session)
    search_result = get_game_by_id(result.id,db_session)
    assert search_result.id == GAME.id
    assert search_result.name == GAME.name
    assert search_result.shop ==  GAME.shop
    assert search_result.img_link == GAME.img_link
    assert search_result.link == GAME.link

# Test the delete_game_by_id function
def test_delete_game_by_id(db_session:Session):
    result = create_game(GAME, db_session)
    search_result = get_game_by_id(result.id,db_session)
    assert search_result.id == GAME.id
    result = delete_game_by_id(result.id,db_session)
    search_result = get_game_by_id(search_result.id,db_session)
    assert search_result is None
    