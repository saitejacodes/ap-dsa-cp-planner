import os
from pymongo import MongoClient
from dotenv import load_dotenv
load_dotenv()
client=MongoClient(os.getenv("MONGO_URI"))
db=client["cpplanner"]
users_collection=db["users"]
plans_collection=db["plans"]


