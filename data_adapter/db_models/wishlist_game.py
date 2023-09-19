from sqlalchemy import Column,String,ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from data_adapter.db_models.base_class import Base

class WishlistGame(Base):
    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    game_id = Column(String,ForeignKey('game.id'))
    wishlist_uuid = Column(UUID(as_uuid=True), ForeignKey('wishlist.uuid'))
    wishlist = relationship("Wishlist",back_populates="wishlist_games")
    games = relationship("Game",back_populates="wishlist_games")