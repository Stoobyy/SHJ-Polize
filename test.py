import pymongo
from pymongo import MongoClient

cluster = MongoClient("mongodb+srv://nalin:shjpolize@shj-polize.53wo6.mongodb.net/?retryWrites=true&w=majority")
db = cluster["shj-polize"]
collection = db["hl"]

# collection.insert_one({'_id': 1, "hl": {"499112914578309120": ["sus"]}})
c = collection.find()

for i in c:
    print(i['hl'])