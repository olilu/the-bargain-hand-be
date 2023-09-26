from typing import List


from pydantic_models.wishlist_game import WishlistGameFull
from pydantic_models.wishlist import WishlistFull
from service.utilities.nintendo import NintendoUtilities
from service.utilities.playstation import PlayStationUtilities

class PriceCheckService:
    def __init__(self, wishlist: WishlistFull, wishlist_games: List[WishlistGameFull]):
        self.wishlist = wishlist
        self.wishlist_games = wishlist_games

    def check_bargains(self) -> List[WishlistGameFull]:
        bargains = []
        nintendo_games = [] 
        playstation_games = []
        for game in self.wishlist_games:
            if game.shop == "Nintendo":
                nintendo_games.append(game)
            elif game.shop == "PlayStation":
                playstation_games.append(game)
            else:
                raise ValueError(f"Shop not supported for game {game.name}: {game.shop}, valid shops are: PlayStation, Nintendo")
        if nintendo_games:
            nintendo_utilities = NintendoUtilities(self.wishlist.uuid, self.wishlist.country_code, self.wishlist.language_code)
            bargains += nintendo_utilities.price_check(nintendo_games)
        if playstation_games:
            ps_utilities = PlayStationUtilities(self.wishlist.uuid, self.wishlist.country_code, self.wishlist.language_code)
            bargains += ps_utilities.price_check(playstation_games)
        return bargains