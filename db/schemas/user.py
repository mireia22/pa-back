
def user_schema(user) -> dict:
    return {
        "id": str(user["_id"]),
        "username": user.get("username", ""),
        "password": user.get("password", ""),
        "image": user.get("image", ""),

    }
    

def users_schema(users) -> list:
    return [user_schema(user) for user in users ]

