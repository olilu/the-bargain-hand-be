from pydantic import BaseModel

class Game(BaseModel):
    id: str
    name: str
    shop: str
    img_link: str
    link: str