import pytest
from sqlalchemy.orm import Session

from tests.controller_tests.test_wishlist_controller import WISHLIST2_DICT
from data_adapter.wishlist_game import get_wishlist_game_by_uuid
from config.settings import settings

NINTENDO_GAME= {
    "name": "Abzû",
    "game_id": "70010000012835",
    "wishlist_uuid": "test-uuid",
    "shop": "Nintendo",
    "currency": "CHF",
    "price_new": 60.00,
    "price_old": 60.00,
    "link": "https://www.nintendo.ch/de/Games/Nintendo-Switch-download-software/ABZU-1467719.html",
    "img_link": "https://fs-prod-cdn.nintendo-europe.com/media/images/10_share_images/games_15/nintendo_switch_download_software_1/H2x1_NSwitchDS_Abzu_image1600w.jpg"
}
PLAYSTATION_GAME={
    "name": "Ghost of a Tale",
    "game_id": "EP1302-CUSA14370_00-GHOSTOFATALE0000",
    "wishlist_uuid": "test-uuid",
    "shop": "PlayStation",
    "currency": "CHF",
    "price_new": 60.00,
    "price_old": 60.00,
    "link": "https://store.playstation.com/de-ch/product/EP1302-CUSA14370_00-GHOSTOFATALE0000",
    "img_link": "https://image.api.playstation.com/cdn/EP1302/CUSA14370_00/pz34zcrT5PB1E36hAseLAIu65fF9W4Cd.png"
}

@pytest.mark.api
@pytest.mark.slow
@pytest.mark.skipif(not settings.TEST_RECEIVER_EMAIL, reason="No test receiver email set")
def test_price_check_controller(client, db_session:Session):
    wishlist = WISHLIST2_DICT
    wishlist["email"] = settings.TEST_RECEIVER_EMAIL
    wishlist_response = client.post("/wishlist/create/",json=WISHLIST2_DICT)
    assert wishlist_response.status_code == 200
    wishlist = wishlist_response.json()
    nintendo_game_response = client.post(f"/wishlist/{wishlist['uuid']}/add-game/",json=NINTENDO_GAME)
    assert nintendo_game_response.status_code == 200
    ps_game_response = client.post(f"/wishlist/{wishlist['uuid']}/add-game/",json=PLAYSTATION_GAME)
    assert ps_game_response.status_code == 200
    bargains_response = client.get(f"/wishlist/{wishlist['uuid']}/check-prices/")
    assert bargains_response.status_code == 200
    assert len(bargains_response.json()) == 2
    assert bargains_response.json()[0]["wishlist_uuid"] == wishlist['uuid']
    assert bargains_response.json()[0]["game_id"] == NINTENDO_GAME["game_id"]
    assert bargains_response.json()[0]["price_new"] != NINTENDO_GAME["price_new"]
    print(bargains_response.json()[0]["uuid"])
    assert bargains_response.json()[0]["price_new"] == get_wishlist_game_by_uuid(bargains_response.json()[0]["uuid"],db_session).price_new
    assert bargains_response.json()[1]["game_id"] == PLAYSTATION_GAME["game_id"]
    assert bargains_response.json()[1]["price_new"] != PLAYSTATION_GAME["price_new"]
    assert bargains_response.json()[1]["price_new"] == get_wishlist_game_by_uuid(bargains_response.json()[1]["uuid"],db_session).price_new


