from types import SimpleNamespace

from pydantic_models.wishlist_game import WishlistGameFull
from service.utilities import nintendo
from service.utilities.nintendo import NintendoUtilities


def create_game(nsuid="70010000000001", title="Test Game"):
    eshop = SimpleNamespace(ch_de="https://www.nintendo.ch/game", fr_fr="https://www.nintendo.fr/game")
    return SimpleNamespace(nsuid=nsuid, title=title, eshop=eshop)


def create_wishlist_game(nsuid="70010000000001", price=20.0):
    return WishlistGameFull(
        uuid="wishlist-game",
        wishlist_uuid="wishlist",
        game_id=nsuid,
        name="Test Game",
        shop="Nintendo",
        link="https://www.nintendo.ch/game",
        img_link="https://images.example/game.jpg",
        price_new=price,
        price_old=price,
        currency="CHF",
        on_sale=False,
    )


def create_price(nsuid, value=20.0, sale_value=None):
    return SimpleNamespace(
        nsuid=nsuid,
        value=value,
        sale_value=sale_value,
        currency="CHF",
        on_sale=sale_value is not None,
    )


def test_search_uses_search_metadata_and_one_batch_price_request(monkeypatch):
    utility = NintendoUtilities("wishlist", "CH", "de")
    search_game = create_game()
    monkeypatch.setattr(utility.shop_region, "search_switch_games", lambda query: iter([search_game]))
    monkeypatch.setattr(utility.shop_region, "game_info", lambda nsuid: (_ for _ in ()).throw(AssertionError("detail lookup is unnecessary")))
    monkeypatch.setattr(nintendo.prices, "fetch_prices", lambda country, nsuids: iter([
        (search_game.nsuid, create_price(search_game.nsuid, value=30.0, sale_value=20.0)),
    ]))
    monkeypatch.setattr(utility, "get_image_links", lambda games: {search_game.nsuid: "https://images.example/game.jpg"})

    result = utility.search("Test Game")

    assert len(result) == 1
    assert result[0].price_new == 20.0
    assert result[0].price_old == 30.0
    assert result[0].on_sale is True


def test_search_ignores_results_without_nsuid(monkeypatch):
    utility = NintendoUtilities("wishlist", "CH", "de")
    valid_game = create_game()
    invalid_game = create_game(nsuid=None, title="Mario Kart unavailable result")
    monkeypatch.setattr(utility.shop_region, "search_switch_games", lambda query: iter([invalid_game, valid_game]))
    monkeypatch.setattr(nintendo.prices, "fetch_prices", lambda country, nsuids: iter([
        (valid_game.nsuid, create_price(valid_game.nsuid)),
    ]))
    monkeypatch.setattr(utility, "get_image_links", lambda games: {valid_game.nsuid: "https://images.example/game.jpg"})

    result = utility.search("Test Game")

    assert [game.game_id for game in result] == [valid_game.nsuid]


def test_price_check_batches_prices_and_reuses_stored_image(monkeypatch):
    utility = NintendoUtilities("wishlist", "CH", "de")
    game = create_wishlist_game(price=30.0)
    calls = []

    def fetch_prices(country, nsuids):
        calls.append(list(nsuids))
        return iter([(game.game_id, create_price(game.game_id, value=30.0, sale_value=20.0))])

    monkeypatch.setattr(nintendo.prices, "fetch_prices", fetch_prices)
    monkeypatch.setattr(utility.shop_region, "game_info", lambda nsuid: (_ for _ in ()).throw(AssertionError("detail lookup is unnecessary")))

    cheaper, updated = utility.price_check([game])

    assert calls == [[game.game_id]]
    assert cheaper[0].price_new == 20.0
    assert updated == []
    assert cheaper[0].img_link == game.img_link


def test_price_check_skips_games_without_a_price(monkeypatch):
    utility = NintendoUtilities("wishlist", "CH", "de")
    game = create_wishlist_game()
    monkeypatch.setattr(nintendo.prices, "fetch_prices", lambda country, nsuids: iter([]))

    cheaper, updated = utility.price_check([game])

    assert cheaper == []
    assert updated == []