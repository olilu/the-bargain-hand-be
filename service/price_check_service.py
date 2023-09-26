from typing import List
from sqlalchemy.orm import Session


from pydantic_models.wishlist_game import WishlistGameFull, WishlistGame
from pydantic_models.wishlist import WishlistFull
from service.utilities.nintendo import NintendoUtilities
from service.utilities.playstation import PlayStationUtilities
from data_adapter.wishlist_game import update_wishlist_game_by_uuid
from service.utilities.email import send_email

class PriceCheckService:
    def __init__(self, wishlist: WishlistFull, wishlist_games: List[WishlistGameFull]):
        self.wishlist = wishlist
        self.wishlist_games = wishlist_games

    def check_bargains(self, db: Session) -> List[WishlistGameFull]:
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
        if bargains:
            update_prices_in_db(bargains, db)
            send_email(self.wishlist.email, bargains)
        return bargains
    
def update_prices_in_db(bargains: List[WishlistGameFull], db: Session):
    for bargain in bargains:
        wishlist_game = WishlistGame(
            uuid=bargain.uuid,
            game_id=bargain.game_id,
            wishlist_uuid=bargain.wishlist_uuid,
            price_old=bargain.price_old,
            price_new=bargain.price_new,
            on_sale=bargain.on_sale,
            currency=bargain.currency,
        )
        update_wishlist_game_by_uuid(bargain.uuid, wishlist_game, db)
