import pymongo
from pymongo import MongoClient
import json


CONNECTION_STRING = "mongodb+srv://ke:ke@cluster0.xdgvl.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
DATABASE = "myFirstDatabase"
SENSOR_DATA_COLLECTION = "sensor_data"
PREDICTED_VALUES_COLLECTION = "predicted_eval_string"

"""
This is the class that interacts with the database server of the dashboard
"""
class DashboardServer():
    def __init__(self):
        print("hello")
        self.connectionString = CONNECTION_STRING
        self.database = self.getDatabase()
        self.sensorCollection = self.database[SENSOR_DATA_COLLECTION]

        self.predictedCollection = self.database[PREDICTED_VALUES_COLLECTION]
        #self.predictedCollection.drop()
        self.sensorCollection.drop()
        

    def printCollection(self):
        cursor = self.sensorCollection
        for document in cursor.find():
            print(document)

    def getDatabase(self):
        client = MongoClient(self.connectionString)
        database = client[DATABASE]
        return database

    def insertPredictedValues(self, predictedValues):
        self.predictedCollection.insert_one(predictedValues)


    def insertSensorValues(self, sensorValue):
        self.sensorCollection.insert_one(sensorValue)


    
if __name__ == "__main__":    
    
    # Get the database
    dashboard = DashboardServer()
    #dbname = dashboard.get_database()