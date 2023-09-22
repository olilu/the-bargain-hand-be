from nintendeals import noe, noa, noj
from nintendeals.api import prices
from bs4 import BeautifulSoup
from typing import List
import requests
import difflib

from pydantic_models.wishlist_game import WishlistGameFull

class NintendoUtilities:
    def __init__(self, wishlist_uuid: str, country_code: str, language_code: str):
        self.wishlist_uuid = wishlist_uuid
        self.country_code = country_code
        self.language_code = language_code
        self.country_language_code = f"{country_code.lower()}_{language_code.lower()}"
        self.shop_region = decide_shop_region(country_code)
    
    def search(self, query: str) -> List[WishlistGameFull]:
        games = []
        search_results = [result for result in self.shop_region.search_switch_games(query)]
        closest_matches = filter_closest_matches(query, search_results)
        for game in closest_matches:
            game_info = self.shop_region.game_info(game.nsuid)
            game_price_info = prices.get_price(game, country=self.country_code.upper())
            wishlist_game = compile_nintendo_wishlist_game(game_info, game_price_info, self.wishlist_uuid, self.country_language_code)
            games.append(wishlist_game)
        return games
    
    def get_game_info_by_nsuid(self, nsuid: str) -> WishlistGameFull:
        game_info = self.shop_region.game_info(nsuid)
        game_price_info = prices.get_price(game_info, country=self.country_code.upper())
        wishlist_game = compile_nintendo_wishlist_game(game_info, game_price_info, "test_uuid", self.country_language_code)
        return wishlist_game
    
def decide_shop_region(country_code: str):
    if country_code.upper() in ["US", "CA", "MX"]:
        shop_region = noa
    elif country_code.upper() in ["JP"]:
        shop_region = noj
    else:
        shop_region = noe
    return shop_region

def scrape_nintendo_image_link(url: str) -> str:
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    return soup.find("vc-price-box-overlay")[":demo-img-src"].replace("'","")

def compile_nintendo_wishlist_game(game_info, game_price_info, wishlist_uuid: str, country_language_code: str) -> WishlistGameFull:
    if game_price_info.on_sale:
        new_price = game_price_info.sale_value
    else:
        new_price = game_price_info.value
    game_link = getattr(game_info.eshop, country_language_code)
        
    wishlist_game = WishlistGameFull(
        wishlist_uuid=wishlist_uuid,
        game_id=game_info.nsuid,
        name=game_info.title,
        shop="Nintendo",
        link=game_link,
        img_link=scrape_nintendo_image_link(game_link),
        price_new=new_price,
        price_old=game_price_info.value,
        on_sale=game_price_info.on_sale,
        currency=game_price_info.currency,
        country_code=game_price_info.country
    )
    return wishlist_game

def filter_closest_matches(query:str, game_list: list, limit=10) -> list:
    titles= [game.title for game in game_list]
    closest_matches_titles = difflib.get_close_matches(query, titles, n=limit, cutoff=0.1)
    closest_matches = [game for game in game_list if game.title in closest_matches_titles]
    def get_index(element):
        return closest_matches_titles.index(element.title)
    closest_matches = sorted(closest_matches, key=get_index)
    return closest_matches

