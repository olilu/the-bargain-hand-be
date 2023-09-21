from sqlalchemy.orm import Session
from datetime import datetime

from pydantic_models.game import Game
from pydantic_models.wishlist_game import WishlistGame
from tests.data_adapter_tests.test_wishlist import create_test_wishlist
from tests.data_adapter_tests.test_game import GAME, GAME2
from data_adapter.game import create_game
from data_adapter.wishlist import create_new_wishlist
from data_adapter.wishlist_game import link_game_to_wishlist, get_wishlist_game_by_uuid, get_wishlist_games_by_wishlist_uuid, unlink_game_from_wishlist, get_wishlist_links_by_game_id, update_wishlist_game_by_uuid

# Test data
WISHLIST = create_test_wishlist()

WISHLIST2 = create_test_wishlist()
WISHLIST2.name = "test wishlist 2"
WISHLIST2.email = "test2@test.com"

def create_test_wishlist_game(wishlist_uuid: str, game_id: str):
    wishlist_game = WishlistGame(
        wishlist_uuid=wishlist_uuid,
        game_id=game_id,
        price_new=10.0,
        price_old=20.0,
    )
    return wishlist_game  

# Test linking a game to a wishlist
def test_link_game_to_wishlist(db_session:Session):
    wishlist_result = create_new_wishlist(WISHLIST,db_session)
    game_result = create_game(GAME,db_session)
    wishlist_game = create_test_wishlist_game(wishlist_result.uuid, game_result.id)
    result = link_game_to_wishlist(wishlist_game,db_session)
    search_result = get_wishlist_game_by_uuid(result.uuid,db_session)
    assert search_result.wishlist_uuid == wishlist_game.wishlist_uuid
    assert search_result.game_id == wishlist_game.game_id
    assert search_result.price_new == wishlist_game.price_new
    assert search_result.price_old == wishlist_game.price_old
    assert search_result.uuid == result.uuid

# Test unlinking a game from a wishlist
def test_unlink_game_from_wishlist(db_session:Session):
    wishlist_result = create_new_wishlist(WISHLIST,db_session)
    game_result = create_game(GAME,db_session)
    wishlist_game = create_test_wishlist_game(wishlist_result.uuid, game_result.id)
    result_link = link_game_to_wishlist(wishlist_game,db_session)
    search_result = get_wishlist_game_by_uuid(result_link.uuid,db_session)
    assert search_result.wishlist_uuid == wishlist_game.wishlist_uuid
    assert search_result.game_id == wishlist_game.game_id
    result_unlink = unlink_game_from_wishlist(wishlist_result.uuid, game_result.id, db_session)
    assert result_unlink == True
    search_result = get_wishlist_game_by_uuid(result_link.uuid,db_session)
    assert search_result is None


# Test get full wishlist games infos by wishlist uuid
def test_get_wishlist_games_by_wishlist_uuid(db_session:Session):
    wishlist_result = create_new_wishlist(WISHLIST,db_session)
    game_result = create_game(GAME,db_session)
    game2_result = create_game(GAME2,db_session)
    wishlist_game = create_test_wishlist_game(wishlist_result.uuid, game_result.id)
    wishlist_game2 = create_test_wishlist_game(wishlist_result.uuid, game2_result.id)
    result_link = link_game_to_wishlist(wishlist_game,db_session)
    result_link2 = link_game_to_wishlist(wishlist_game2,db_session)
    # get wishlist games infos by wishlist uuid
    print("wishlist_result.uuid: ",wishlist_result.uuid)
    result = get_wishlist_games_by_wishlist_uuid(wishlist_result.uuid,db_session)
    # Ensure return of full info wishlist games
    assert len(result) == 2
    assert result[0].wishlist_uuid == wishlist_game.wishlist_uuid
    assert result[0].game_id == wishlist_game.game_id
    assert result[0].price_new == result_link.price_new
    assert result[0].price_old == result_link.price_old
    assert result[0].name == GAME.name
    assert result[0].shop == GAME.shop
    assert result[0].img_link == GAME.img_link
    assert result[0].link == GAME.link
    assert result[1].wishlist_uuid == wishlist_game2.wishlist_uuid
    assert result[1].game_id == wishlist_game2.game_id
    assert result[1].price_new == result_link2.price_new
    assert result[1].price_old == result_link2.price_old
    assert result[1].name == GAME2.name
    assert result[1].shop == GAME2.shop
    assert result[1].img_link == GAME2.img_link
    assert result[1].link == GAME2.link

# Test get wishlist links by game id
def test_get_wishlist_links_by_game_id(db_session:Session):
    wishlist_result = create_new_wishlist(WISHLIST,db_session)
    wishlist_result2 = create_new_wishlist(WISHLIST2,db_session)
    game_result = create_game(GAME,db_session)
    wishlist_game = create_test_wishlist_game(wishlist_result.uuid, game_result.id)
    wishlist_game2 = create_test_wishlist_game(wishlist_result2.uuid, game_result.id)
    wishlist_game2.price_new = 5.0
    result_link = link_game_to_wishlist(wishlist_game,db_session)
    result_link2 = link_game_to_wishlist(wishlist_game2,db_session)
    # get wishlist links by game id
    result = get_wishlist_links_by_game_id(game_result.id,db_session)
    # Ensure return of full info wishlist games
    assert len(result) == 2
    assert result[0].wishlist_uuid == wishlist_result.uuid
    assert result[0].game_id == game_result.id
    assert result[1].wishlist_uuid == wishlist_result2.uuid
    assert result[1].game_id == game_result.id
    assert result[1].price_new == wishlist_game2.price_new


# Test update wishlist game by uuid
def test_update_wishlist_game_by_uuid(db_session:Session):
    wishlist_result = create_new_wishlist(WISHLIST,db_session)
    game_result = create_game(GAME,db_session)
    wishlist_game = create_test_wishlist_game(wishlist_result.uuid, game_result.id)
    result_link = link_game_to_wishlist(wishlist_game,db_session)
    # Update the wishlist game
    wishlist_game.price_new = 5.0
    result = update_wishlist_game_by_uuid(result_link.uuid,wishlist_game,db_session)
    # Check that the wishlist game is updated
    search_result = get_wishlist_game_by_uuid(result_link.uuid,db_session)
    assert result == True
    assert search_result.price_new == 5.0
    assert search_result.price_old == 20.0

    