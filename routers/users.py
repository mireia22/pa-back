from fastapi import APIRouter, status, HTTPException
from db.models.user import User
from db.config import userCollection, attractionCollection
from db.schemas.user import user_schema, users_schema
from bson import ObjectId
from typing import List
from db.models.attraction import  GoneRequest, RatingRequest, TimesRequest

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}}
)

# Helper function to search user in MongoDB
def search_user(field: str, key):
    try:
        if field == "_id":
            key = ObjectId(key)  # Convert to ObjectId if searching by _id
        user = userCollection.find_one({field: key})
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return User(**user_schema(user))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# GET: Retrieve a user by ID (path parameter)
@router.get("/user/{id}", response_model=User)
async def get_user_by_id(id: str):
    return search_user("_id", id)


# Helper function to search user by ID and name
def search_user_by_id_and_name(id: str, name: str):
    try:
        user = userCollection.find_one({"_id": ObjectId(id), "name": name})
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return User(**user_schema(user))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

# GET: Retrieve all users
@router.get("/", response_model=List[User])
async def get_all_users():
    users = users_schema(userCollection.find())
    return users



# GET: Retrieve a user by ID (query parameter)
@router.get("/userbyid", response_model=User)
async def get_user_by_id_query(id: str):
    return search_user("_id", id)

# GET: Retrieve a user by ID and name (query parameters)
@router.get("/userbyidandname", response_model=User)
async def get_user_by_id_and_name_query(id: str, name: str):
    return search_user_by_id_and_name(id, name)

# POST: Create a new user
@router.post("/user", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user: User):
    # Check if the user already exists
    existing_user = userCollection.find_one({"username": user.username})
    
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")
    
    # Insert the new user
    user_dict = user.dict()
    result = userCollection.insert_one(user_dict)
    
    new_user = user_schema(userCollection.find_one({"_id": result.inserted_id}))
    
    return User(**new_user)

# PUT: Update a user
@router.put("/user/{id}", response_model=User)
async def update_user(id: str, user: User):
    user_dict = user.dict(exclude_unset=True)  # Exclude fields not sent in the request
    user_dict.pop("id", None)  # Don't allow modifying the ID

    result = userCollection.find_one_and_update(
        {"_id": ObjectId(id)},
        {"$set": user_dict},
        return_document=True
    )

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return search_user("_id", id)

# DELETE: Delete a user
@router.delete("/user/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(id: str):
    result = userCollection.find_one_and_delete({"_id": ObjectId(id)})
    
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return {"message": "User deleted successfully"}


@router.get("/user/{username}/attractions", response_model=User)
async def get_user_attractions(username: str):
    user = userCollection.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user_schema(user) 









@router.patch("/user/{id}/avatar")
async def update_avatar(id: str, avatar_data: dict):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid user ID")
    
    user = userCollection.find_one({"_id": ObjectId(id)})
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    avatar_url = avatar_data.get("image")
    
    if not avatar_url:
        raise HTTPException(status_code=400, detail="Invalid image URL")

    userCollection.update_one({"_id": ObjectId(id)}, {"$set": {"image": avatar_url}})
    
    return {"message": "Avatar updated successfully", "image": avatar_url}





@router.patch("/user/{username}/update_want_to_go/{attraction_id}")
async def update_want_to_go(username: str, attraction_id: str):
    # Encuentra el usuario
    user = userCollection.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Encuentra la atracción
    attraction = attractionCollection.find_one({"_id": ObjectId(attraction_id)})
    if not attraction:
        raise HTTPException(status_code=404, detail="Attraction not found")

    # Verifica si la atracción ya está en la lista 'attractions_want'
    if any(a["_id"] == attraction_id for a in user["attractions_want"]):
        # Si la atracción ya está, la eliminamos
        update_result = userCollection.update_one(
            {"username": username},
            {"$pull": {"attractions_want": {"_id": attraction_id}}}
        )
    else:
        # Si no está, la añadimos con toda su información
        update_result = userCollection.update_one(
            {"username": username},
            {"$addToSet": {"attractions_want": {
                "_id": attraction_id,
                "name": attraction["name"],
                "image": attraction["image"],
                "area": attraction["area"]
            }}}
        )

    if update_result.modified_count == 0:
        raise HTTPException(status_code=500, detail="Failed to update attractions_want")

    # Devuelve la lista actualizada de 'attractions_want'
    updated_user = userCollection.find_one({"username": username}, {"_id": 0, "attractions_want": 1})
    return {"message": "Updated successfully", "attractions_want": updated_user.get("attractions_want")}


@router.patch("/user/{username}/update_gone/{attraction_id}")
async def update_gone(username: str, attraction_id: str):
    user = userCollection.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    
    attraction = attractionCollection.find_one({"_id": ObjectId(attraction_id)})
    if not attraction:
        raise HTTPException(status_code=404, detail="Attraction not found")

    # Verifica si la atracción ya está en la lista 'attractions_gone'
    if any(a["_id"] == attraction_id for a in user["attractions_gone"]):
        # Si la atracción ya está, la eliminamos
        update_result = userCollection.update_one(
            {"username": username},
            {"$pull": {"attractions_gone": {"_id": attraction_id}}}
        )
    else:
        # Si no está, la añadimos con toda su información
        update_result = userCollection.update_one(
            {"username": username},
            {"$addToSet": {"attractions_gone": {
                "_id": attraction_id,
                "name": attraction["name"],
                "image": attraction["image"],
                "area": attraction["area"],
                "rating": attraction.get("rating", 0)  ,    
                "times": attraction.get("times", 0)  

            }}}
        )

    if update_result.modified_count == 0:
        raise HTTPException(status_code=500, detail="Failed to update attractions_gone")

    # Devuelve la lista actualizada de 'attractions_gone'
    updated_user = userCollection.find_one({"username": username}, {"_id": 0, "attractions_gone": 1})
    return {"message": "Updated successfully", "attractions_gone": updated_user.get("attractions_gone")}



@router.patch("/user/{username}/delete_want/{attraction_id}")
async def delete_want(username: str, attraction_id: str):
    user = userCollection.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Remove the attraction from the 'attractions_want' array
    update_result = userCollection.update_one(
        {"username": username},
        {"$pull": {"attractions_want": {"_id": attraction_id}}}
    )
    
    if update_result.modified_count == 0:
        raise HTTPException(status_code=500, detail="Failed to delete attraction from 'attractions_want'")
    
    # Return the updated list of 'attractions_want'
    updated_user = userCollection.find_one({"username": username}, {"_id": 0, "attractions_want": 1})
    return {"message": "Deleted successfully", "attractions_want": updated_user.get("attractions_want")}





@router.patch("/user/{username}/update_rating/{attraction_id}")
async def update_rating(username: str, attraction_id: str, request: RatingRequest):
    user = userCollection.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if the attraction exists in the user's attractions_gone list
    found = False
    for attraction in user.get("attractions_gone", []):
        if attraction["_id"] == attraction_id:
            attraction["rating"] = request.rating
            found = True
            break

    # If found, update the database
    if found:
        userCollection.update_one({"username": username}, {"$set": {"attractions_gone": user["attractions_gone"]}})
        return {"message": "Updated successfully"}
    
    # Return an error if the attraction isn't found in the "gone" list
    raise HTTPException(status_code=404, detail="Attraction not found in 'gone' list")



@router.patch("/user/{username}/update_times/{attraction_id}")
async def update_rating(username: str, attraction_id: str, request: TimesRequest):
    user = userCollection.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if the attraction exists in the user's attractions_gone list
    found = False
    for attraction in user.get("attractions_gone", []):
        if attraction["_id"] == attraction_id:
            attraction["times"] = request.times
            found = True
            break

    # If found, update the database
    if found:
        userCollection.update_one({"username": username}, {"$set": {"attractions_gone": user["attractions_gone"]}})
        return {"message": "Updated successfully"}
    
    # Return an error if the attraction isn't found in the "gone" list
    raise HTTPException(status_code=404, detail="Attraction not found in 'gone' list")



