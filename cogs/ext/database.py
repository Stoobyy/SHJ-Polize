import os
from pymongo import MongoClient

cluster = MongoClient(os.environ["MONGO"])
db = cluster["shj-polize"]