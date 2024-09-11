from pydantic import BaseModel
from typing import Optional, List
from db.models.attraction import Attraction, AttractionWithRating

class User(BaseModel):
    id: Optional[str] = None
    username: str
    password: str
    image: Optional[str] = None
    attractions_want: List[Attraction] = [] 
    attractions_gone: List[AttractionWithRating] = [] 
