from pydantic import BaseModel
from typing import Optional

class WishlistGameBase(BaseModel):
    uuid: Optional[str] = None
    wishlist_uuid: Optional[str] = None
    game_id: Optional[str] = None
    price_old: Optional[float] = None
    price_new: Optional[float] = None
    currency: Optional[str] = "CHF"

class WishlistGame(WishlistGameBase):
    wishlist_uuid: str
    game_id: str

# combination of WishlistGame and Game
class WishlistGameFull(WishlistGame):
    name: str
    shop: str
    img_link: str
    link: str