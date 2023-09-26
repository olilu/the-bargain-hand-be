from typing import List


from pydantic_models.wishlist_game import WishlistGameFull
from pydantic_models.wishlist import WishlistFull
from service.utilities.nintendo import NintendoUtilities
from service.utilities.playstation import PlayStationUtilities

class SearchService:
    def __init__(self, wishlist: WishlistFull):
        self.wishlist = wishlist

    def get_search_service(self, shop: str):
        if shop == "Nintendo":
            return NintendoUtilities(self.wishlist.uuid, self.wishlist.country_code, self.wishlist.language_code)
        elif shop == "PlayStation":
            return PlayStationUtilities(self.wishlist.uuid, self.wishlist.country_code, self.wishlist.language_code)
        else:
            raise ValueError(f"Shop not supported: {shop}, valid shops are: PlayStation, Nintendo")

    def search(self, query: str, shop: str) -> List[WishlistGameFull]:
        games = []
        shop_utilities = self.get_search_service(shop)
        games = shop_utilities.search(query)
        return games
    


