from pydantic import BaseModel,AnyHttpUrl

class Game(BaseModel):
    id: str
    name: str
    shop: str
    img_link: str
    link: str