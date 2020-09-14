import pymongo
import time
import json


def monsend(topic,count,location):
  # If connection is not initialized, initialize it.
  #if not config.initialized:
  client = pymongo.MongoClient("mongodb+srv://Melody:Password1@group6-wwzz1.mongodb.net/test?retryWrites=true&w=majority")
  db = client.Twitter
  if location=='us':
    collection = db['USA']
  else:
    collection = db[location]
  timeNow = time.time()
  collection.insert_one({"time":timeNow,"tag":topic,"count":count})

def monsendmany(records,location):
  client = pymongo.MongoClient(
    "mongodb+srv://Melody:Password1@group6-wwzz1.mongodb.net/test?retryWrites=true&w=majority")
  db = client.Twitter
  collection = db[location]
  collection.drop()
  #records.write.format("com.mongodb.spark.sql.DefaultSource").mode("append").save()
  #print(type(json.loads(records.T.to_json()).values()))
  #print(json.loads(records.T.to_json()).values())

  collection.insert_many(json.loads(records.T.to_json()).values())


