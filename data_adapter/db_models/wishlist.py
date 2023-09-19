from sqlalchemy import Column,String,DateTime,Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from data_adapter.db_models.base_class import Base

class Wishlist(Base):
    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String,nullable=False)
    email = Column(String,nullable=False,index=True)
    schedule_timestamp = Column(DateTime,nullable=False)
    schedule_frequency = Column(Integer,nullable=False,default=1)
    country_code = Column(String,nullable=False,default="CH")
    wishlist_game = relationship("WishlistGame",back_populates="wishlist")
