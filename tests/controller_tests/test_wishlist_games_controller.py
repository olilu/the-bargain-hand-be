import pytest

from pydantic_models.game import Game
from tests.controller_tests.test_wishlist_controller import WISHLIST_DICT
from tests.data_adapter_tests.test_game import GAME, GAME2


def generate_test_game_dict(wishlist_uuid: str, game: Game):
    game_dict =   {
        "wishlist_uuid": wishlist_uuid,
        "game_id": game.id,
        "price_old": 22.20,
        "price_new": 15.90,
        "currency": "CHF",
        "name": game.name,
        "shop": game.shop,
        "img_link": game.img_link,
        "link": game.link,
        "on_sale": True
    }
    return game_dict

# Test the /wishlist/{wishlist_uuid}/games endpoint
@pytest.mark.api
def test_return_full_wishlist_games(client):
    response = client.post("/wishlist/create/",json=WISHLIST_DICT)
    assert response.status_code == 200
    uuid = response.json()["uuid"]
    game_dict = generate_test_game_dict(uuid,GAME)
    game2_dict = generate_test_game_dict(uuid,GAME2)
    # link games to wishlist
    response = client.post("/wishlist/"+uuid+"/add-game",json=game_dict)
    assert response.status_code == 200
    response = client.post("/wishlist/"+uuid+"/add-game",json=game2_dict)
    assert response.status_code == 200
    # get games from wishlist
    response = client.get("/wishlist/"+uuid+"/games")
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["wishlist_uuid"] == uuid
    assert response.json()[0]["game_id"] == game_dict["game_id"]
    assert response.json()[1]["wishlist_uuid"] == uuid
    assert response.json()[1]["game_id"] == game2_dict["game_id"]

# Test the /wishlist/{wishlist_uuid}/add-game endpoint
@pytest.mark.api
def test_add_game_to_wishlist(client):
    response = client.post("/wishlist/create/",json=WISHLIST_DICT)
    assert response.status_code == 200
    uuid = response.json()["uuid"]
    game_dict = generate_test_game_dict(uuid,GAME)
    # link a game to a wishlist
    response = client.post("/wishlist/"+uuid+"/add-game",json=game_dict)
    assert response.status_code == 200
    print(response.json())
    assert response.json()["wishlist_uuid"] == uuid
    assert response.json()["game_id"] == game_dict["game_id"]
    assert response.json()["price_new"] == game_dict["price_new"]
    assert response.json()["price_old"] == game_dict["price_old"]
    assert response.json()["currency"] == game_dict["currency"]
    assert response.json()["on_sale"] == game_dict["on_sale"]
    # link a game to a wishlist that already has the game
    response = client.post("/wishlist/"+uuid+"/add-game",json=game_dict)
    assert response.status_code == 409
    # link a game to a non-existing wishlist
    response = client.post("/wishlist/not-existing-uuid/add-game",json=game_dict)
    assert response.status_code == 404

# Test the /wishlist/{wishlist_uuid}/remove-game/{game_id} endpoint
@pytest.mark.api
def test_remove_game_from_wishlist(client):
    response = client.post("/wishlist/create/",json=WISHLIST_DICT)
    assert response.status_code == 200
    uuid = response.json()["uuid"]
    game_dict = generate_test_game_dict(uuid,GAME)
    # link a game to a wishlist
    response = client.post("/wishlist/"+uuid+"/add-game",json=game_dict)
    assert response.status_code == 200
    # remove a game from a wishlist
    response = client.delete("/wishlist/"+uuid+"/remove-game/"+game_dict["game_id"])
    assert response.status_code == 200
    assert response.json()["details"] == "game successfully removed from wishlist"
    # remove a game from a wishlist that does not have the game
    response = client.delete("/wishlist/"+uuid+"/remove-game/"+game_dict["game_id"])
    assert response.status_code == 404
    # remove a game from a non-existing wishlist
    response = client.delete("/wishlist/not-existing-uuid/remove-game/"+game_dict["game_id"])
    assert response.status_code == 404
    # remove a non-existing game from a wishlist
    response = client.delete("/wishlist/"+uuid+"/remove-game/not-existing-game-id")
    assert response.status_code == 404