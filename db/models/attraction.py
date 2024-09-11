from pydantic import BaseModel
from typing import Optional, List

class Attraction(BaseModel):
    name: str
    area: str
    image: Optional[str] = None
    times: Optional[int] = None

class AttractionWithRating(Attraction):
    rating: Optional[int] = None
    
    
class WantToGoRequest(BaseModel):
    want_to_go: bool
    
        
class GoneRequest(BaseModel):
    gone: bool
    rating: Optional[int] = None
    times:  Optional[int] = None
    
class RatingRequest(BaseModel):
    rating: int
    
class TimesRequest(BaseModel):
    times: int