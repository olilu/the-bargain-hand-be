from typing import List
import requests
import asyncio
import aiohttp
import re
import json
import logging
import iso4217parse

from pydantic_models.wishlist_game import WishlistGameFull
from service.utilities.shop import ShopUtilities

class PlayStationUtilities(ShopUtilities):
    # PlayStation's search page no longer server-renders results, it fetches them client-side
    # via this persisted GraphQL query. The hash is tied to the current store frontend build
    # and may need to be refreshed if PlayStation ships a new one (search would return nothing).
    GRAPHQL_URL = "https://web.np.playstation.com/api/graphql/v1/op"
    SEARCH_OPERATION_NAME = "getSearchResults"
    SEARCH_PERSISTED_QUERY_HASH = "4df6284f982e57bec70f23c77e2c219dc792eb19af7fb3d3a81767aa3f1958aa"

    def __init__(self, wishlist_uuid: str, country_code: str, language_code: str):
        super().__init__(wishlist_uuid, country_code, language_code)
        self.base_url = "https://store.playstation.com"
        self.country_language_code = f"{language_code.lower()}-{country_code.lower()}"
        self.search_url = f"{self.base_url}/{self.country_language_code}/search/"
        self.product_url = f"{self.base_url}/{self.country_language_code}/product/"
        self.currency = iso4217parse.by_country(self.country_code)[0].alpha3
    
    def search(self, query: str) -> List[WishlistGameFull]:
        response = self.search_playstation_api(query)
        return [self.compile_game(result) for result in response]
    
    def price_check(self, game_list: List[WishlistGameFull]) -> tuple[List[WishlistGameFull], List[WishlistGameFull]]:
        loop = get_or_create_eventloop()
        updated_game_list = loop.run_until_complete(self.check_games_async(game_list))
        valid_games = [game for game in updated_game_list if game is not None]
        cheaper_games, updated_games = self.compare_prices(game_list, valid_games)
        return cheaper_games, updated_games

    def scrape_playstation_search_results(self, query: str) -> List[WishlistGameFull]:
        return [self.compile_game(result) for result in self.search_playstation_api(query)]

    def search_playstation_api(self, query: str) -> List[dict]:
        variables = {
            "countryCode": self.country_code.upper(),
            "languageCode": self.language_code.lower(),
            "nextCursor": "",
            "pageOffset": 0,
            "pageSize": 10,
            "searchTerm": query,
        }
        extensions = {
            "persistedQuery": {
                "version": 1,
                "sha256Hash": self.SEARCH_PERSISTED_QUERY_HASH,
            }
        }
        params = {
            "operationName": self.SEARCH_OPERATION_NAME,
            "variables": json.dumps(variables),
            "extensions": json.dumps(extensions),
        }
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json",
            # bypasses PlayStation's Apollo CSRF check for cross-origin GET requests
            "apollo-require-preflight": "true",
        }
        r = requests.get(self.GRAPHQL_URL, params=params, headers=headers, timeout=30)
        r.raise_for_status()
        return r.json().get("data", {}).get("universalSearch", {}).get("results", []) or []

    def compile_game(self, result: dict, original_game: WishlistGameFull = None) -> WishlistGameFull:
        game_id = original_game.game_id if original_game else result.get("id")
        product = self.get_available_product(result)
        product_id = product.get("id") if product else None
        price = (product or result).get("price") or {}
        price_new = self.parse_price(price.get("discountedPrice"))
        price_old = self.parse_price(price.get("basePrice"))
        if price_old == 0.0:
            price_old = price_new
        on_sale = price_new < price_old
        link_id = product_id or result.get("id") or game_id
        link_type = "product" if product_id else "concept"
        return WishlistGameFull(
            uuid=original_game.uuid if original_game else None,
            wishlist_uuid=self.wishlist_uuid,
            game_id=game_id,
            name=result.get("name") or (original_game.name if original_game else "Unknown"),
            shop="PlayStation",
            link=f"{self.base_url}/{self.country_language_code}/{link_type}/{link_id}",
            img_link=self.pick_search_result_image(result.get("media", [])) or (original_game.img_link if original_game else ""),
            price_new=price_new,
            price_old=price_old,
            on_sale=on_sale,
            currency=self.currency,
        )

    @staticmethod
    def get_available_product(result: dict) -> dict:
        if result.get("__typename") == "Product":
            return result
        products = result.get("products") or []
        return products[0] if products else None

    @staticmethod
    def parse_price(value: str) -> float:
        if not value:
            return 0.0
        match = re.search(r"\d+(?:[.,]\d{1,2})?", value.replace("'", ""))
        return float(match.group(0).replace(",", ".")) if match else 0.0

    async def check_games_async(self, games: List[WishlistGameFull]) -> List[WishlistGameFull]:
        async with aiohttp.ClientSession() as session:
            results = await asyncio.gather(
                *(self.check_game_async(session, game) for game in games),
                return_exceptions=True,
            )
        valid_results = []
        for game, result in zip(games, results):
            if isinstance(result, Exception):
                logging.warning("Could not check PlayStation game %s: %s", game.game_id, result)
                continue
            valid_results.append(result)
        return valid_results

    async def check_game_async(self, session: aiohttp.ClientSession, game: WishlistGameFull) -> WishlistGameFull:
        variables = {
            "countryCode": self.country_code.upper(),
            "languageCode": self.language_code.lower(),
            "nextCursor": "",
            "pageOffset": 0,
            "pageSize": 10,
            "searchTerm": game.name,
        }
        extensions = {"persistedQuery": {"version": 1, "sha256Hash": self.SEARCH_PERSISTED_QUERY_HASH}}
        params = {
            "operationName": self.SEARCH_OPERATION_NAME,
            "variables": json.dumps(variables),
            "extensions": json.dumps(extensions),
        }
        headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json", "apollo-require-preflight": "true"}
        async with session.get(self.GRAPHQL_URL, params=params, headers=headers, timeout=30) as response:
            response.raise_for_status()
            payload = await response.json()
        results = payload.get("data", {}).get("universalSearch", {}).get("results", []) or []
        result = next((item for item in results if item.get("id") == game.game_id), None)
        if result is None and game.game_id.isdigit():
            result = next((item for item in results if item.get("__typename") == "Concept" and item.get("name") == game.name), None)
        if result is None:
            result = next((item for item in results if item.get("__typename") == "Product" and item.get("name") == game.name), None)
        if result is None:
            raise ValueError(f"PlayStation game not found in API: {game.name}")
        return self.compile_game(result, game)

    def pick_search_result_image(self, media: List[dict]) -> str:
        for role in ("GAMEHUB_COVER_ART", "FOUR_BY_THREE_BANNER", "EDITION_KEY_ART"):
            for item in media:
                if item.get("role") == role and item.get("type") == "IMAGE":
                    return item.get("url")
        for item in media:
            if item.get("type") == "IMAGE":
                return item.get("url")
        return None

    
def get_or_create_eventloop():
    try:
        return asyncio.get_event_loop()
    except RuntimeError as ex:
        if "There is no current event loop in thread" in str(ex):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return asyncio.get_event_loop()