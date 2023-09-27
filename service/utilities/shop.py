from typing import List
import logging

from pydantic_models.wishlist_game import WishlistGameFull

class ShopUtilities:
    def __init__(self, wishlist_uuid: str, country_code: str, language_code: str):
        self.wishlist_uuid = wishlist_uuid
        self.country_code = country_code
        self.language_code = language_code
        self.country_language_code = f"{country_code.lower()}_{language_code.lower()}"

    def compare_prices(self, db_games: List[WishlistGameFull], new_games: List[WishlistGameFull]) -> (List[WishlistGameFull], List[WishlistGameFull]):
        cheaper_games = []
        changed_games = []
        for db_game in db_games:
            for new_game in new_games:
                if db_game.game_id == new_game.game_id:
                    if db_game.price_new != new_game.price_new:
                        logging.warning(f"Price changed for {new_game.name}: {db_game.price_new} -> {new_game.price_new}")
                        new_game.uuid = db_game.uuid
                        # in case the game price changed without being on sale, we need to update the old price
                        if new_game.price_old == new_game.price_new:
                            logging.warning(f"Price changed for {new_game.name} without being on sale: {db_game.price_new} -> {new_game.price_new}")
                            new_game.price_old = db_game.price_new
                        if db_game.price_new > new_game.price_new:
                            logging.warning(f"Price dropped for {new_game.name}: {db_game.price_new} -> {new_game.price_new}")
                            cheaper_games.append(new_game)
                        else:
                            logging.warning(f"Price increased for {new_game.name}: {db_game.price_new} -> {new_game.price_new}")
                            changed_games.append(new_game)
        return cheaper_games, changed_games
        