import pytest
import re

from service.search_service import SearchService
from pydantic_models.wishlist import WishlistFull

PRICE_REGEX = r"^\d+(.\d{1,2})"

WISHLIST = WishlistFull(
        uuid="test_uuid",
        name="test_name",
        email="test@example.com",
        schedule_timestamp="2023-09-20T17:05:10.173031",
        schedule_frequency=1,
        country_code="CH",
        language_code="de",
    )

@pytest.mark.integration
@pytest.mark.slow
def test_nintendo_search():
    search_service = SearchService(
        wishlist=WISHLIST
    )
    search_results = search_service.search(query="Abzû",shop="Nintendo")
    assert "Abzû".upper() in [game.name for game in search_results]

    assert search_results[0].game_id == "70010000012835"
    assert search_results[0].wishlist_uuid == "test_uuid"
    assert search_results[0].shop == "Nintendo"
    assert search_results[0].currency == "CHF"
    assert re.match(PRICE_REGEX, str(search_results[0].price_new))
    assert re.match(PRICE_REGEX, str(search_results[0].price_old))
    assert search_results[0].link == 'https://www.nintendo.ch/de/Games/Nintendo-Switch-download-software/ABZU-1467719.html'
    assert search_results[0].img_link == 'https://fs-prod-cdn.nintendo-europe.com/media/images/10_share_images/games_15/nintendo_switch_download_software_1/H2x1_NSwitchDS_Abzu_image1600w.jpg'

@pytest.mark.integration
@pytest.mark.slow
def test_playstation_search():
    search_service = SearchService(
        wishlist=WISHLIST
    )
    search_results = search_service.search(query="ghost of a tale",shop="PlayStation")
    assert "Ghost of a Tale" in [game.name for game in search_results]

    assert search_results[0].game_id == "EP1302-CUSA14370_00-GHOSTOFATALE0000"
    assert search_results[0].wishlist_uuid == "test_uuid"
    assert search_results[0].shop == "PlayStation"
    assert search_results[0].currency == "CHF"
    assert re.match(PRICE_REGEX, str(search_results[0].price_new))    
    assert re.match(PRICE_REGEX, str(search_results[0].price_old))
    assert search_results[0].link == 'https://store.playstation.com/de-ch/product/EP1302-CUSA14370_00-GHOSTOFATALE0000'
    assert search_results[0].img_link == 'https://image.api.playstation.com/cdn/EP1302/CUSA14370_00/pz34zcrT5PB1E36hAseLAIu65fF9W4Cd.png'

@pytest.mark.integration
def test_unknown_shop_search():
    search_service = SearchService(
        wishlist=WISHLIST
    )
    with pytest.raises(ValueError):
        search_service.search(query="Abzû",shop="Unknown")

