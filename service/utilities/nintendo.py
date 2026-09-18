from nintendeals import noe, noa, noj
from nintendeals.api import prices
from bs4 import BeautifulSoup
from typing import Dict, List
import requests
import difflib
import logging
import iso4217parse
from concurrent.futures import ThreadPoolExecutor

from service.utilities.shop import ShopUtilities
from pydantic_models.wishlist_game import WishlistGameFull

class NintendoUtilities(ShopUtilities):
    def __init__(self, wishlist_uuid: str, country_code: str, language_code: str):
        super().__init__(wishlist_uuid, country_code, language_code)
        self.shop_region = self.get_nintendo_shop_region()
    
    def search(self, query: str) -> List[WishlistGameFull]:
        search_results = [
            game for game in self.shop_region.search_switch_games(query)
            if game.nsuid
        ]
        search_results = filter_closest_matches(query, search_results)
        price_by_nsuid = self.get_prices([game.nsuid for game in search_results])
        image_by_nsuid = self.get_image_links(search_results)
        games = []
        for game in search_results:
            games.append(self.compile_nintendo_wishlist_game(
                game,
                price_by_nsuid.get(game.nsuid),
                image_by_nsuid.get(game.nsuid),
            ))
        return games
    
    def price_check(self, game_list: List[WishlistGameFull]) -> tuple[List[WishlistGameFull], List[WishlistGameFull]]:
        price_by_nsuid = self.get_prices([game.game_id for game in game_list])
        updated_game_list = []
        for game in game_list:
            game_price_info = price_by_nsuid.get(game.game_id)
            if game_price_info is None:
                logging.warning("Could not retrieve Nintendo price for %s", game.game_id)
                continue
            updated_game_list.append(self.compile_price_update(game, game_price_info))
        cheaper_games, updated_games = self.compare_prices(game_list, updated_game_list)
        return cheaper_games,updated_games
    
    def get_game_info_by_id(self, nsuid: str) -> WishlistGameFull:
        game_info = self.shop_region.game_info(nsuid)
        game_price_info = prices.get_price(game_info, country=self.country_code.upper()) if game_info else None
        return self.compile_nintendo_wishlist_game(game_info, game_price_info)

    def get_prices(self, nsuids: List[str]) -> Dict[str, object]:
        if not nsuids:
            return {}
        price_by_nsuid = {}
        unique_nsuids = list(dict.fromkeys(nsuids))
        for start in range(0, len(unique_nsuids), 50):
            batch = unique_nsuids[start:start + 50]
            try:
                price_by_nsuid.update(prices.fetch_prices(
                    country=self.country_code.upper(),
                    nsuids=batch,
                ))
            except Exception as error:
                logging.warning("Could not retrieve Nintendo prices for batch: %s", error)
        return price_by_nsuid

    def get_image_links(self, games: List[object]) -> Dict[str, str]:
        def fetch_image(game):
            try:
                return game.nsuid, scrape_nintendo_image_link(self.get_game_link(game))
            except Exception as error:
                logging.warning("Could not retrieve Nintendo image for %s: %s", game.nsuid, error)
                return game.nsuid, "https://placehold.co/400x400"

        with ThreadPoolExecutor(max_workers=min(10, max(1, len(games)))) as executor:
            return dict(executor.map(fetch_image, games))
    
    def get_nintendo_shop_region(self):
        if self.country_code.upper() in ["US", "CA", "MX"]:
            shop_region = noa
        elif self.country_code.upper() in ["JP"]:
            shop_region = noj
        else:
            shop_region = noe
        return shop_region
    
    def compile_nintendo_wishlist_game(self, game_info, game_price_info, image_link=None) -> WishlistGameFull:
        if game_info is None:
            raise ValueError("Nintendo game information is missing")
        if game_price_info is None:
            currency = iso4217parse.by_country(self.country_code)[0].alpha3
            new_price = old_price = 0.0
            on_sale = False
        elif game_price_info.on_sale:
            new_price = game_price_info.sale_value
            old_price = game_price_info.value
            on_sale = True
        else:
            new_price = game_price_info.value
            old_price = game_price_info.value
            on_sale = False
        game_link = self.get_game_link(game_info)
            
        wishlist_game = WishlistGameFull(
            wishlist_uuid=self.wishlist_uuid,
            game_id=game_info.nsuid,
            name=game_info.title,
            shop="Nintendo",
            link=game_link,
            img_link=image_link or scrape_nintendo_image_link(game_link),
            price_new=new_price,
            price_old=old_price,
            on_sale=on_sale,
            currency=game_price_info.currency if game_price_info is not None else currency
        )
        return wishlist_game

    def get_game_link(self, game_info) -> str:
        if self.country_code.upper() == "GB":
            return getattr(game_info.eshop, "uk_en")
        return getattr(game_info.eshop, self.country_language_code)

    def compile_price_update(self, game: WishlistGameFull, game_price_info) -> WishlistGameFull:
        new_price = game_price_info.sale_value if game_price_info.on_sale else game_price_info.value
        return game.model_copy(update={
            "price_new": new_price,
            "price_old": game_price_info.value,
            "on_sale": game_price_info.on_sale,
            "currency": game_price_info.currency,
        })

def scrape_nintendo_image_link(url: str) -> str:
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, 'html.parser')
    try:
        return soup.find("vc-price-box-overlay")[":demo-img-src"].replace("'","")
    except TypeError:
        return "https://placehold.co/400x400"

def filter_closest_matches(query:str, game_list: list, limit=10) -> list:
    titles = [(game.title).lower() for game in game_list]
    closest_matches_titles = difflib.get_close_matches(query.lower(), titles, n=limit, cutoff=0.1)
    closest_matches = [game for game in game_list if (game.title).lower() in closest_matches_titles]
    def get_index(element):
        return closest_matches_titles.index(element.title.lower())
    closest_matches = sorted(closest_matches, key=get_index)
    return closest_matches

