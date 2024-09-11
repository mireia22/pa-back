from fastapi import APIRouter
from db.models.attraction import Attraction
from db.config import attractionCollection
from db.schemas.attraction import attraction_schema, convertAttractions

router = APIRouter(prefix="/attractions", 
                               tags=["attractions"],
                               responses={404: {"message": "Not found"}})




# GET
# get all attractions 
@router.get("/all_attractions")
def getAllAttractions():
    attractions_cursor = attractionCollection.find()
    attractions = list(attractions_cursor)  # Convert cursor to a list of documents
    convertedAttractisons = convertAttractions(attractions)
    return {"status": "Ok", "data": convertedAttractisons}


@router.get("/areas")
def get_areas():
    areas = attractionCollection.distinct("area")
    return {"status": "Ok", "data": areas}

@router.get("/attractions_by_area/{area}")
def get_attractions_by_area(area: str):
    attractions_cursor = attractionCollection.find({"area": area})
    attractions = list(attractions_cursor)  
    convertedAttractions = convertAttractions(attractions)
    print("convertedatractions",convertedAttractions)
    return {"status": "Ok", "data": convertedAttractions}

