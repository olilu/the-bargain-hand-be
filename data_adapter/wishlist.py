from sqlalchemy.orm import Session
import uuid

from pydantic_models.wishlist import WishlistCreate, WishlistUpdate
from data_adapter.db_models.wishlist import Wishlist

def create_new_wishlist(wishlist:WishlistCreate,db:Session):
    wishlist_model = wishlist.model_dump()
    wishlist_model["uuid"] = str(uuid.uuid4())
    wishlist_entry = Wishlist(**wishlist_model)
    db.add(wishlist_entry)
    db.commit()
    db.refresh(wishlist_entry)
    return wishlist_entry

def list_wishlists(db:Session):
    wishlists = db.query(Wishlist).all()
    return wishlists

def delete_wishlist(wishlist_uuid:str,db:Session):
    wishlist = db.query(Wishlist).filter(Wishlist.uuid == wishlist_uuid).first()
    db.delete(wishlist)
    db.commit()
    return wishlist

def get_wishlist(wishlist_uuid:str,db:Session):
    return db.query(Wishlist).filter(Wishlist.uuid == wishlist_uuid).first()

def update_wishlist(wishlist:WishlistUpdate,db:Session):
    wishlist_model = wishlist.model_dump()
    print(wishlist_model)
    existing_wishlist = db.query(Wishlist).filter(Wishlist.uuid == wishlist.uuid)
    if existing_wishlist.first() is None:
        return False
    existing_wishlist.update(wishlist_model)
    db.commit()
    return True

