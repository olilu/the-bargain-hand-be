from sqlalchemy.orm import Session
import pytest

from config.settings import settings
from service.price_check_service import run_price_checks_all_wishlists
from tests.data_adapter_tests.test_wishlist import create_test_wishlist
from tests.data_adapter_tests.test_game import GAME, GAME2
from tests.data_adapter_tests.test_wishlist_game import create_test_wishlist_game
from data_adapter.wishlist import create_new_wishlist
from data_adapter.game import create_game
from data_adapter.wishlist_game import link_game_to_wishlist

@pytest.mark.manual
@pytest.mark.skipif(not settings.TEST_RECEIVER_EMAIL, reason="No test receiver email set")
@pytest.mark.skip(reason="This test needs manual checking")
def test_run_price_check_all_wishlists(db_session:Session):
    wishlist = create_test_wishlist()
    wishlist.email = settings.TEST_RECEIVER_EMAIL
    wishlist_result = create_new_wishlist(wishlist,db_session)
    game_result = create_game(GAME,db_session)
    wishlist_game = create_test_wishlist_game(wishlist_result.uuid, game_result.id, price_old=5.0, price_new=5.0)
    link_game_to_wishlist(wishlist_game,db_session)
    game_result = create_game(GAME2,db_session)
    wishlist_game = create_test_wishlist_game(wishlist_result.uuid, game_result.id, price_old=50.0, price_new=50.0)
    link_game_to_wishlist(wishlist_game,db_session)
    run_price_checks_all_wishlists(db_session)
    assert True