from sqlalchemy import Column,String,ForeignKey,Double,Boolean
from sqlalchemy.orm import relationship

from data_adapter.db_models.base_class import Base

class WishlistGame(Base):
    uuid = Column(String, primary_key=True)
    game_id = Column(String,ForeignKey('game.id'))
    wishlist_uuid = Column(String, ForeignKey('wishlist.uuid'))
    price_old = Column(Double,nullable=True)
    price_new = Column(Double,nullable=True)
    on_sale = Column(Boolean,nullable=True, default=False)
    currency = Column(String(3),nullable=False,default="CHF")
    wishlist = relationship("Wishlist",back_populates="wishlist_game")
    game = relationship("Game",back_populates="wishlist_game")
