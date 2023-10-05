import pytest


from service.utilities.email import send_email
from pydantic_models.wishlist_game import WishlistGameFull
from config.settings import settings

BARGAIN1 = WishlistGameFull(
    uuid="test-uuid",
    wishlist_uuid="test-wishlist-uuid",
    game_id="EP1302-CUSA14370_00-GHOSTOFATALE0000",
    price_old=25.90,
    price_new=12.95,
    currency="CHF",
    on_sale=True,
    name="Ghost of a Tale",
    shop="PlayStation",
    img_link="https://image.api.playstation.com/cdn/EP1302/CUSA14370_00/pz34zcrT5PB1E36hAseLAIu65fF9W4Cd.png",
    link="https://store.playstation.com/de-ch/product/EP1302-CUSA14370_00-GHOSTOFATALE0000"
    )

BARGAIN2 = WishlistGameFull(
    uuid="test-uuid",
    wishlist_uuid="test-wishlist-uuid",
    game_id="EP2333-PPSA01826_00-PATHLESSSIEE0000",
    price_old=39.90,
    price_new=19.95,
    currency="CHF",
    on_sale=True,
    name="The Pathless",
    shop="PlayStation",
    img_link="https://image.api.playstation.com/vulcan/ap/rnd/202007/1500/PzzL4lymRdZuLEerjeL58HG8.png",
    link="https://store.playstation.com/de-ch/product/EP2333-PPSA01826_00-PATHLESSSIEE0000"
)

BARGAIN3 = WishlistGameFull(
    uuid="test-uuid",
    wishlist_uuid="test-wishlist-uuid",
    game_id="70010000012835",
    price_old=19.99,
    price_new=9.99,
    currency="CHF",
    on_sale=True,
    name="Abzû",
    shop="Nintendo",
    img_link="https://fs-prod-cdn.nintendo-europe.com/media/images/10_share_images/games_15/nintendo_switch_download_software_1/H2x1_NSwitchDS_Abzu_image1600w.jpg",
    link="https://www.nintendo.ch/de/Games/Nintendo-Switch-download-software/ABZU-1467719.html"
)

@pytest.mark.manual
@pytest.mark.skipif(not settings.TEST_RECEIVER_EMAIL, reason="No test receiver email set")
@pytest.mark.skip(reason="Manual test")
def test_send_email():
    bargains = [BARGAIN1,BARGAIN2,BARGAIN3]
    send_email(settings.TEST_RECEIVER_EMAIL,bargains, "de_CH")
    assert True