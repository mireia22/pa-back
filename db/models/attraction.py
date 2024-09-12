from pydantic import BaseModel
from typing import Optional, List

class Attraction(BaseModel):
    id: Optional[str] = None  # Asegúrate de que el ID esté incluido
    name: str
    area: str
    image: Optional[str] = None
    times: Optional[int] = 1
    want_to_go: Optional[bool] = True  # Indica si el usuario quiere ir
    gone: Optional[bool] = False  # Indica si el usuario ya ha ido
    rating: Optional[int] = 0  # Rating por defecto

class AttractionWithRating(Attraction):
    rating: Optional[int] = None
    
    
class WantToGoRequest(BaseModel):
    want_to_go: bool
    
        
class GoneRequest(BaseModel):
    gone: bool
    rating: Optional[int] = None
    times:  Optional[int] = 1
    
class RatingRequest(BaseModel):
    rating: int
    
class TimesRequest(BaseModel):
    times: int