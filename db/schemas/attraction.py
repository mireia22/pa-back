def attraction_schema(attraction):
    return {
        "id": str(attraction["_id"]),
        "name": attraction.get("name", ""),
        "area": attraction.get("area", ""),
        "image": f"/static{attraction['image']}" ,
        "want_to_go": attraction.get("want_to_go", False),  
        "gone": attraction.get("gone", False),  
        "rating": attraction.get("rating", 0)  ,
        "times": attraction.get("times", 0)  
}


def convertAttractions(attractions):
    return [attraction_schema(attraction) for attraction in attractions]
