from fastapi import FastAPI
from routers import attractions, users, jwt_auth
from starlette.middleware.cors import CORSMiddleware

from fastapi.staticfiles import StaticFiles
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(attractions.router)
app.include_router(users.router)
app.include_router(jwt_auth.router)

# http://127.0.0.1:8000/static/images/woody.png
# app.mount("/static", StaticFiles(directory="static"), name="static")

# Mount the public directory to serve static files
app.mount("/static", StaticFiles(directory="public"), name="static")

@app.get("/",tags=["Root"])
async def hello():
    return {"message": "Hello World"}