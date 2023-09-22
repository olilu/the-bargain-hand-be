from sqlalchemy import Column,String,DateTime,Integer
from sqlalchemy.orm import relationship

from data_adapter.db_models.base_class import Base

class Wishlist(Base):
    uuid = Column(String, primary_key=True)
    name = Column(String,nullable=False)
    email = Column(String,nullable=False,index=True)
    schedule_timestamp = Column(DateTime,nullable=False)
    schedule_frequency = Column(Integer,nullable=False,default=1)
    country_code = Column(String(2),nullable=False,default="CH")
    language_code = Column(String(2),nullable=False,default="de")
    wishlist_game = relationship("WishlistGame",back_populates="wishlist")
