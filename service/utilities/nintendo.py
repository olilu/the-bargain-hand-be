from nintendeals import noe, noa, noj
from nintendeals.api import prices
from bs4 import BeautifulSoup
from typing import List
import requests
import difflib
import time
import iso4217parse

from service.utilities.shop import ShopUtilities
from pydantic_models.wishlist_game import WishlistGameFull

class NintendoUtilities(ShopUtilities):
    def __init__(self, wishlist_uuid: str, country_code: str, language_code: str):
        super().__init__(wishlist_uuid, country_code, language_code)
        self.shop_region = self.get_nintendo_shop_region()
    
    def search(self, query: str) -> List[WishlistGameFull]:
        start_time = time.time()
        games = []
        search_results = [result for result in self.shop_region.search_switch_games(query)]
        time_difference = time.time() - start_time
        print(f'search time: %.2f seconds.' % time_difference)
        closest_matches = filter_closest_matches(query, search_results)
        for game in closest_matches:
            game_info = self.shop_region.game_info(game.nsuid)
            try:
                game_price_info = prices.get_price(game_info, country=self.country_code.upper())
            except:
                game_price_info = {
                    "on_sale": False,
                    "sale_value": 0,
                    "value": 0,
                    "currency": iso4217parse.by_country(self.country_code)[0].alpha3
                }
            wishlist_game = self.compile_nintendo_wishlist_game(game_info, game_price_info)
            games.append(wishlist_game)
        time_difference = time.time() - start_time
        print(f'Scraping time: %.2f seconds.' % time_difference)
        return games
    
    def price_check(self, game_list: List[WishlistGameFull]) -> (List[WishlistGameFull], List[WishlistGameFull]):
        updated_game_list = []
        for game in game_list:
            game_info = self.get_game_info_by_id(game.game_id)
            updated_game_list.append(game_info)
        cheaper_games, updated_games = self.compare_prices(game_list, updated_game_list) 
        return cheaper_games,updated_games
    
    def get_game_info_by_id(self, nsuid: str) -> WishlistGameFull:
        game_info = self.shop_region.game_info(nsuid)
        game_price_info = prices.get_price(game_info, country=self.country_code.upper())
        return self.compile_nintendo_wishlist_game(game_info, game_price_info)   
    
    def get_nintendo_shop_region(self):
        if self.country_code.upper() in ["US", "CA", "MX"]:
            shop_region = noa
        elif self.country_code.upper() in ["JP"]:
            shop_region = noj
        else:
            shop_region = noe
        return shop_region
    
    def compile_nintendo_wishlist_game(self, game_info, game_price_info) -> WishlistGameFull:
        if game_price_info.on_sale:
            new_price = game_price_info.sale_value
        else:
            new_price = game_price_info.value
        if self.country_code.upper() == "GB":
            game_link = getattr(game_info.eshop, "uk_en")
        else:
            game_link = getattr(game_info.eshop, self.country_language_code)
            
        wishlist_game = WishlistGameFull(
            wishlist_uuid=self.wishlist_uuid,
            game_id=game_info.nsuid,
            name=game_info.title,
            shop="Nintendo",
            link=game_link,
            img_link=scrape_nintendo_image_link(game_link),
            price_new=new_price,
            price_old=game_price_info.value,
            on_sale=game_price_info.on_sale,
            currency=game_price_info.currency
        )
        return wishlist_game

def scrape_nintendo_image_link(url: str) -> str:
    r = requests.get(url)
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

