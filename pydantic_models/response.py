from pydantic import BaseModel

class GenericResponse(BaseModel):
    details: str