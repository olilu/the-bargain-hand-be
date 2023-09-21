from pydantic import BaseModel

class GenericResponse(BaseModel):
    detail: str