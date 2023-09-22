import pytest


from service.search_service import SearchService

@pytest.mark.integration
@pytest.mark.slow
def test_nintendo_search():
    search_service = SearchService(
        wishlist_uuid="test_uuid",
        country_code="CH",
        language_code="de"
    )
    search_results = search_service.search(query="Abzû",shop="Nintendo")
    assert "Abzû".upper() in [game.name for game in search_results]

    assert search_results[0].game_id == "70010000012835"
    assert search_results[0].wishlist_uuid == "test_uuid"
    assert search_results[0].shop == "Nintendo"
    assert search_results[0].currency == "CHF"
    assert search_results[0].link == 'https://www.nintendo.ch/de/Games/Nintendo-Switch-download-software/ABZU-1467719.html'
    assert search_results[0].img_link == 'https://fs-prod-cdn.nintendo-europe.com/media/images/10_share_images/games_15/nintendo_switch_download_software_1/H2x1_NSwitchDS_Abzu_image1600w.jpg'


