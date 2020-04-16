#!/usr/bin/python3
import pymongo


class Mongo:
    def __init__(self, host, port, database_name):
        self.client = pymongo.MongoClient(f"mongodb://{host}:{port}/")
        self.db = self.client[database_name]

    def collection(self, collection):
        collection = self.db[collection]
        return collection

    def insert(self, collection, data):
        collection = self.db[collection]
        result = collection.insert_one(data)
        return result

    def find(self, collection, filter, limit=-1, ascendingSort="", descendingSort=""):
        collection = self.db[collection]

        if ascendingSort != "":
            if limit > 0:
                result = collection.find(filter).sort(
                    ascendingSort).limit(limit)
            else:
                result = collection.find(filter).sort(
                    ascendingSort)
        elif descendingSort != "":
            if limit > 0:
                result = collection.find(filter).sort(
                    descendingSort, -1).limit(limit)
            else:
                result = collection.find(filter).sort(
                    descendingSort, -1)
        else:
            if limit > 0:
                result = collection.find(filter).limit(limit)
            else:
                result = collection.find(filter)
        return result

    def find_one(self, collection, filter):
        collection = self.db[collection]
        result = collection.find_one(filter)
        return result

    def update(self, collection, filter, data):
        collection = self.db[collection]
        result = collection.update(filter, data)
        return result

    def aggregate(self, collection, filter):
        collection = self.db[collection]
        result = collection.aggregate(filter)
        return result
