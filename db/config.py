
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
from dotenv import load_dotenv
from constants.attractions import portaventura_attractions

# Load environment variables from .env file
load_dotenv()
uri = os.getenv("MONGODB_URI")

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

db = client.portAventura

userCollection = db['users']

attractionCollection = db['attractions']
existing_attractions_count = attractionCollection.count_documents({})


# Insert attractions if the collection is empty
if existing_attractions_count == 0:
    result = attractionCollection.insert_many(portaventura_attractions)
    print(f"Inserted {len(result.inserted_ids)} documents into the collection.")
else:
    print(f"Attractions already exist in the database. No need to insert again.")



# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)