from typing import Optional
from pydantic import BaseModel,EmailStr,constr
from datetime import datetime

class WishlistBase(BaseModel):
    uuid: Optional[str] = None
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    schedule_frequency: Optional[int] = 1
    schedule_timestamp: Optional[datetime] = datetime.now()
    country_code: Optional[constr(max_length=2, to_upper=True)] = "CH"
    language_code: Optional[constr(max_length=2, to_lower=True)] = "de"

class WishlistCreate(WishlistBase):
    name: str
    email: EmailStr

class WishlistShow(WishlistBase):
    name: str
    email: EmailStr
    schedule_frequency: int
    schedule_timestamp: datetime
    country_code: constr(max_length=2, to_upper=True)
    language_code: constr(max_length=2, to_lower=True)

class WishlistUpdate(WishlistShow):
    uuid: str