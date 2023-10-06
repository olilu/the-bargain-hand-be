from typing import List
import logging
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
        to_update = []
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
            cheaper, updated = nintendo_utilities.price_check(nintendo_games)
            bargains.extend(cheaper)
            to_update.extend(updated)
        if playstation_games:
            ps_utilities = PlayStationUtilities(self.wishlist.uuid, self.wishlist.country_code, self.wishlist.language_code)
            cheaper, updated = ps_utilities.price_check(playstation_games)
            bargains.extend(cheaper)
            to_update.extend(updated)
        if bargains:
            logging.warning(f"Alerting {len(bargains)} bargains to {self.wishlist.email}")
            to_update.extend(bargains)
            send_email(self.wishlist.email, bargains)
        if to_update:
            logging.warning(f"Updating {len(to_update)} games in db")
            update_prices_in_db(to_update, db)
        return bargains
    
def update_prices_in_db(games: List[WishlistGameFull], db: Session):
    for game in games:
        wishlist_game = WishlistGame(
            uuid=game.uuid,
            game_id=game.game_id,
            wishlist_uuid=game.wishlist_uuid,
            price_old=game.price_old,
            price_new=game.price_new,
            on_sale=game.on_sale,
            currency=game.currency,
        )
        update_wishlist_game_by_uuid(game.uuid, wishlist_game, db)


def run_price_checks_all_wishlists(db: Session):
    from data_adapter.wishlist import list_wishlists
    from data_adapter.wishlist_game import get_wishlist_games_by_wishlist_uuid
    wishlists = list_wishlists(db)
    for wishlist in wishlists:
        logging.warning(f"Checking prices for {wishlist.name} ({wishlist.uuid})")
        logging.warning(f"Country {wishlist.country_code}, language {wishlist.language_code}")
        wishlist_games = get_wishlist_games_by_wishlist_uuid(wishlist.uuid, db)
        price_check_service = PriceCheckService(
            wishlist=wishlist,
            wishlist_games=wishlist_games
        )
        bargains = price_check_service.check_bargains(db=db)
        logging.warning(f"Found {len(bargains)} bargains for {wishlist.name}")

