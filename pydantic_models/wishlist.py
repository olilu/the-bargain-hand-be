from typing import Optional
from pydantic import BaseModel,EmailStr,UUID4
from datetime import datetime,time


class WishlistBase(BaseModel):
    uuid: Optional[UUID4] = None
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    schedule_frequency: Optional[int] = 1
    schedule_timestamp: Optional[time] = datetime.now().time()
    country_code: Optional[str] = "CH"

class WishlistCreate(WishlistBase):
    name: str
    email: EmailStr
    country_code: str