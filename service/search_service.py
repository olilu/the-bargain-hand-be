from typing import List


from pydantic_models.wishlist_game import WishlistGameFull
from service.utilities.nintendo import NintendoUtilities
from service.utilities.playstation import PlayStationUtilities

class SearchService:
    def __init__(self, wishlist_uuid: str, country_code: str, language_code: str):
        self.wishlist_uuid = wishlist_uuid
        self.country_code = country_code
        self.language_code = language_code

    def search(self, query: str, shop: str) -> List[WishlistGameFull]:
        games = []
        if shop == "Nintendo":
            nintendo_utilities = NintendoUtilities(self.wishlist_uuid, self.country_code, self.language_code)
            games = nintendo_utilities.search(query)
        elif shop == "PlayStation":
            ps_utilities = PlayStationUtilities(self.wishlist_uuid, self.country_code, self.language_code)
            games = ps_utilities.search(query)
        else:
            raise ValueError(f"Shop not supported: {shop}, valid shops are: PlayStation, Nintendo")
        return games
    


