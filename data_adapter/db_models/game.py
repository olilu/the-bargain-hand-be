from sqlalchemy import Column,String
from sqlalchemy.orm import relationship

from data_adapter.db_models.base_class import Base

class Game(Base):
    id = Column(String, primary_key=True)
    shop = Column(String, nullable=False)
    img_link = Column(String, nullable=False, default="https://via.placeholder.com/150")
    link = Column(String, nullable=False, unique=True)
    wishlist_game = relationship("WishlistGame",back_populates="game")