from sqlalchemy.orm import Session

from pydantic_models.wishlist import WishlistCreate
from data_adapter.db_models.wishlist import Wishlist

def create_new_wishlist(wishlist:WishlistCreate,db:Session):
    wishlist = Wishlist(**wishlist.model_dump())
    db.add(wishlist)
    db.commit()
    db.refresh(wishlist)
    return wishlist

def list_wishlists(db:Session):
    wishlists = db.query(Wishlist).all()
    return wishlists