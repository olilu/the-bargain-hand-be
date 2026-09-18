import asyncio

from pydantic_models.wishlist_game import WishlistGameFull
from service.utilities.playstation import PlayStationUtilities


def create_utility():
    return PlayStationUtilities("wishlist", "CH", "de")


def create_game(game_id="10014611", name="Tales of Eternia Remastered"):
    return WishlistGameFull(
        uuid="game-uuid",
        wishlist_uuid="wishlist",
        game_id=game_id,
        name=name,
        shop="PlayStation",
        link="https://store.playstation.com/de-ch/concept/10014611",
        img_link="https://image.api.playstation.com/concept.jpg",
        price_new=0.0,
        price_old=0.0,
        currency="CHF",
        on_sale=False,
    )


def test_concept_without_product_has_zero_price():
    utility = create_utility()
    result = utility.compile_game({
        "__typename": "Concept",
        "id": "10014611",
        "name": "Tales of Eternia Remastered",
        "media": [],
        "products": [],
        "price": None,
    })

    assert result.game_id == "10014611"
    assert result.price_new == 0.0
    assert result.price_old == 0.0
    assert result.link.endswith("/concept/10014611")


def test_available_concept_uses_product_url_and_price():
    utility = create_utility()
    result = utility.compile_game({
        "__typename": "Concept",
        "id": "10014611",
        "name": "Tales of Eternia Remastered",
        "media": [],
        "products": [{
            "id": "EP0000-PPSA00000_00-ETERNIA00000000",
            "price": {"basePrice": "CHF 59.90", "discountedPrice": "CHF 39.90"},
        }],
    }, create_game())

    assert result.game_id == "10014611"
    assert result.price_new == 39.90
    assert result.price_old == 59.90
    assert result.on_sale is True
    assert result.link.endswith("/product/EP0000-PPSA00000_00-ETERNIA00000000")


def test_async_check_keeps_successful_games_when_one_fails():
    utility = create_utility()
    games = [create_game("10014611"), create_game("10014612", "Other Game")]

    async def check_game(_session, game):
        if game.game_id == "10014611":
            raise RuntimeError("temporary PlayStation API failure")
        return game

    utility.check_game_async = check_game
    result = asyncio.run(utility.check_games_async(games))

    assert result == [games[1]]