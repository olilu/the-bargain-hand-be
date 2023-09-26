import pytest
import re

from tests.controller_tests.test_wishlist_controller import WISHLIST2_DICT
from tests.service_tests.test_search_service import PRICE_REGEX

@pytest.mark.api
@pytest.mark.slow
def test_search_game_nintendo(client):
    query = "Abzû"
    shop = "Nintendo"
    wishlist_response = client.post("/wishlist/create/",json=WISHLIST2_DICT)
    assert wishlist_response.status_code == 200
    search_response = client.get("/search/game?query="+query+"&shop="+shop+"&wishlist_uuid="+wishlist_response.json()['uuid'])
    assert search_response.status_code == 200
    assert len(search_response.json()) > 0
    assert search_response.json()[0]["name"] == query.upper()
    assert search_response.json()[0]["game_id"] == "70010000012835"
    assert search_response.json()[0]["wishlist_uuid"] == wishlist_response.json()["uuid"]
    assert search_response.json()[0]["shop"] == shop
    assert search_response.json()[0]["currency"] == "CHF"
    assert re.match(PRICE_REGEX, str(search_response.json()[0]["price_new"]))
    assert re.match(PRICE_REGEX, str(search_response.json()[0]["price_old"]))
    assert search_response.json()[0]["link"] == 'https://www.nintendo.ch/de/Games/Nintendo-Switch-download-software/ABZU-1467719.html'
    assert search_response.json()[0]["img_link"] == 'https://fs-prod-cdn.nintendo-europe.com/media/images/10_share_images/games_15/nintendo_switch_download_software_1/H2x1_NSwitchDS_Abzu_image1600w.jpg'


@pytest.mark.api
@pytest.mark.slow
def test_search_game_playstation(client):
    query = "ghost of a tale"
    shop = "PlayStation"
    wishlist_response = client.post("/wishlist/create/",json=WISHLIST2_DICT)
    assert wishlist_response.status_code == 200
    search_response = client.get("/search/game?query="+query+"&shop="+shop+"&wishlist_uuid="+wishlist_response.json()['uuid'])
    assert search_response.status_code == 200
    assert len(search_response.json()) > 0
    assert search_response.json()[0]["name"] == "Ghost of a Tale"
    assert search_response.json()[0]["game_id"] == "EP1302-CUSA14370_00-GHOSTOFATALE0000"
    assert search_response.json()[0]["wishlist_uuid"] == wishlist_response.json()["uuid"]
    assert search_response.json()[0]["shop"] == shop
    assert search_response.json()[0]["currency"] == "CHF"
    assert re.match(PRICE_REGEX, str(search_response.json()[0]["price_new"]))
    assert re.match(PRICE_REGEX, str(search_response.json()[0]["price_old"]))
    assert search_response.json()[0]["link"] == 'https://store.playstation.com/de-ch/product/EP1302-CUSA14370_00-GHOSTOFATALE0000'
    assert search_response.json()[0]["img_link"] == 'https://image.api.playstation.com/cdn/EP1302/CUSA14370_00/pz34zcrT5PB1E36hAseLAIu65fF9W4Cd.png'