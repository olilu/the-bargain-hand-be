from sqlalchemy import Column,String,ForeignKey
from sqlalchemy.dialects.postgresql import UUID,MONEY
from sqlalchemy.orm import relationship
import uuid

from data_adapter.db_models.base_class import Base

class WishlistGame(Base):
    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    game_id = Column(String,ForeignKey('game.id'))
    wishlist_uuid = Column(UUID(as_uuid=True), ForeignKey('wishlist.uuid'))
    price_old = Column(MONEY,nullable=True)
    price_new = Column(MONEY,nullable=True)
    currency = Column(String(3),nullable=False,default="CHF")
    wishlist = relationship("Wishlist",back_populates="wishlist_game")
    game = relationship("Game",back_populates="wishlist_game")