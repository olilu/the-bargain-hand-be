from sqlalchemy.orm import Session
from datetime import datetime
import pytest

from pydantic_models.wishlist import WishlistCreate
from pydantic_models.wishlist_game import WishlistGame
from data_adapter.wishlist import create_new_wishlist, list_wishlists, delete_wishlist, get_wishlist_by_uuid, update_wishlist
from data_adapter.game import create_game, get_game_by_id
from data_adapter.wishlist_game import link_game_to_wishlist, get_wishlist_game_by_uuid
from tests.data_adapter_tests.test_game import GAME

def create_test_wishlist():
    wishlist = WishlistCreate(
        name="test wishlist",
        email="test@test.com",
        schedule_timestamp=datetime.now(),
        country_code="CH",
        language_code="de"
    )
    return wishlist

# Test the create_new_wishlist function and the list_wishlists function
@pytest.mark.data_adapter
def test_list_wishlists(db_session:Session):
    test_results = []
    # Create a wishlist
    wishlist = create_test_wishlist()
    result = create_new_wishlist(wishlist,db_session)
    test_results.append(result)
    # Create a second wishlist
    wishlist.name = "test wishlist 2"
    wishlist.email = "test2@test.com"
    result = create_new_wishlist(wishlist,db_session)
    test_results.append(result)
    # Call the list_wishlists function
    wishlists = list_wishlists(db_session)
    # Check that the list has length 2
    assert len(wishlists) == 2
    assert wishlists[0].name == "test wishlist"
    assert wishlists[1].name == "test wishlist 2"
    assert wishlists[0].email == "test@test.com"
    assert wishlists[1].email == "test2@test.com"
    assert wishlists[0].country_code == wishlist.country_code
    assert wishlists[1].country_code == wishlist.country_code
    assert wishlists[0].language_code == wishlist.language_code
    assert wishlists[1].language_code == wishlist.language_code
    assert wishlists[0].schedule_frequency == wishlist.schedule_frequency
    assert wishlists[1].schedule_frequency == wishlist.schedule_frequency
    assert wishlists[0].schedule_timestamp == wishlist.schedule_timestamp
    assert wishlists[1].schedule_timestamp == wishlist.schedule_timestamp
    assert wishlists[0].uuid is not None
    assert wishlists[1].uuid is not None

# Test the delete_wishlist function
@pytest.mark.data_adapter
def test_delete_wishlist(db_session:Session):
    # Create a wishlist
    wishlist = create_test_wishlist()
    result = create_new_wishlist(wishlist,db_session)
    # ensure that the wishlist is created
    search_result = get_wishlist_by_uuid(result.uuid,db_session)
    assert search_result.name == "test wishlist"
    # Create games and link them to the wishlist
    game_result = create_game(GAME,db_session)
    assert game_result.id is not None
    wishlist_game = WishlistGame(
        wishlist_uuid=search_result.uuid,
        game_id=game_result.id,
        price_new=10.00,
        price_old=10.00,
        on_sale=False,
    )
    link_result = link_game_to_wishlist(wishlist_game,db_session)
    assert link_result is not None
    # Call the delete_wishlist function
    result = delete_wishlist(result.uuid,db_session)
    assert result == True
    # Check that the wishliste is deleted
    search_result = get_wishlist_by_uuid(search_result.uuid,db_session)
    assert search_result is None
    # Check that the games are deleted
    search_result = get_wishlist_game_by_uuid(link_result.uuid,db_session)
    assert search_result is None
    game_result = get_game_by_id(game_result.id,db_session)
    assert game_result is None
    
# Test the update_wishlist function
@pytest.mark.data_adapter
def test_update_wishlist(db_session:Session):
    # Create a wishlist
    wishlist = create_test_wishlist()
    result = create_new_wishlist(wishlist,db_session)
    # ensure that the wishlist is created
    search_result = get_wishlist_by_uuid(result.uuid,db_session)
    assert search_result.name == "test wishlist"
    assert search_result.country_code == "CH"
    # Update the wishlist
    wishlist.name = "test renamed"
    wishlist.country_code = "US"
    wishlist.language_code = "en"
    update_result = update_wishlist(result.uuid,wishlist,db_session)
    # Check that the wishlist is updated
    search_result = get_wishlist_by_uuid(result.uuid,db_session)
    assert update_result == True
    assert search_result.name == "test renamed"
    assert search_result.country_code == "US"
    assert search_result.language_code == "en"

