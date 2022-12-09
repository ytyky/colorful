from flask import Flask
from flask_pymongo import pymongo
#from app import app
CONNECTION_STRING = ""
client = pymongo.MongoClient(CONNECTION_STRING)
mongodb = client.get_database('colofulDB')