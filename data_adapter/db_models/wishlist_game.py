from sqlalchemy import Column,String,ForeignKey,Double
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from data_adapter.db_models.base_class import Base
# db_models/wishlist_game.py
class WishlistGame(Base):
    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    game_id = Column(String,ForeignKey('game.id'))
    wishlist_uuid = Column(String, ForeignKey('wishlist.uuid'))
    price_old = Column(Double,nullable=True)
    price_new = Column(Double,nullable=True)
    currency = Column(String(3),nullable=False,default="CHF")
    wishlist = relationship("Wishlist",back_populates="wishlist_game")
    game = relationship("Game",back_populates="wishlist_game")