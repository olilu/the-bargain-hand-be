from typing import Optional
from pydantic import BaseModel,EmailStr,ConfigDict
from datetime import datetime

class WishlistBase(BaseModel):
    uuid: Optional[str] = None
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    schedule_frequency: Optional[int] = 1
    schedule_timestamp: Optional[datetime] = datetime.now()
    country_code: Optional[str] = "CH"

class WishlistCreate(WishlistBase):
    name: str
    email: EmailStr
    country_code: str

class WishlistShow(WishlistBase):
    name: str
    email: EmailStr
    schedule_frequency: int
    schedule_timestamp: datetime
    country_code: str

class WishlistUpdate(WishlistShow):
    uuid: str