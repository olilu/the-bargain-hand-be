from typing import List
from enum import Enum


from pydantic_models.wishlist_game import WishlistGameFull
from service.utilities.nintendo import NintendoUtilities

class Shops(Enum):
    Nintendo = "Nintendo"
    PlayStation = "PlayStation"

class SearchService:
    def __init__(self, wishlist_uuid: str, country_code: str, language_code: str):
        self.wishlist_uuid = wishlist_uuid
        self.country_code = country_code
        self.language_code = language_code

    def search(self, query: str, shop: Shops) -> List[WishlistGameFull]:
        games = []
        if shop == "Nintendo":
            nintendo_utilities = NintendoUtilities(self.wishlist_uuid, self.country_code, self.language_code)
            games = nintendo_utilities.search(query)
        elif shop == "PlayStation":
            pass
        else:
            raise ValueError(f"Shop not supported: {shop}, valid shops are: {[e.value for e in Shops]}")
        return games
    


