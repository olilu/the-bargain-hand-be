from sqlalchemy import Column,String,Double,Integer,DateTime,ForeignKey
from sqlalchemy.orm import relationship,as_declarative,declared_attr
from typing import Any
import uuid
from data_adapter.db_models.base_class import Base

@as_declarative()
class TestBase:
    id: Any
    __name__: str

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

class WishlistGame(TestBase):
    uuid = Column(String, primary_key=True, default=uuid.uuid4)
    game_id = Column(String,ForeignKey('game.id'))
    wishlist_uuid = Column(String, ForeignKey('wishlist.uuid'))
    price_old = Column(Double,nullable=True)
    price_new = Column(Double,nullable=True)
    currency = Column(String(3),nullable=False,default="CHF")
    wishlist = relationship("Wishlist",back_populates="wishlist_game")
    game = relationship("Game",back_populates="wishlist_game")

class Wishlist(TestBase):
    uuid = Column(String, primary_key=True, default=uuid.uuid4)
    name = Column(String,nullable=False)
    email = Column(String,nullable=False,index=True)
    schedule_timestamp = Column(DateTime,nullable=False)
    schedule_frequency = Column(Integer,nullable=False,default=1)
    country_code = Column(String,nullable=False,default="CH")
    wishlist_game = relationship("WishlistGame",back_populates="wishlist")

class Game(TestBase):
    id = Column(String, primary_key=True)
    shop = Column(String, nullable=False)
    img_link = Column(String, nullable=False, default="https://via.placeholder.com/150")
    link = Column(String, nullable=False, unique=True)
    wishlist_game = relationship("WishlistGame",back_populates="game")
