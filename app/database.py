from pymongo import MongoClient
from dotenv import load_dotenv
from progress.bar import ChargingBar
import os

load_dotenv()

client = MongoClient(os.environ.get("MONGODB_CONNECTION_STRING"))

# database: university
# collection: exams


def saveExams(exams):
    bar = ChargingBar('Saving exams', max=len(exams))
    for exam in exams:
        client.university.exams.update_one({"_id": exam['id']},
                                           {"$set":
                                            {
                                                "id": exam['id'],
                                                "name": exam["name"],
                                                "year": exam["year"],
                                                "cfu": exam["cfu"],
                                                "frequency": exam["frequency"],
                                                "mark": exam["mark"],
                                                "date": exam["date"]
                                            }
                                            }, upsert=True)
        bar.next()
    bar.finish()
    return {'message': 'Exams saved correctly.'}


def getExams():
    exams = []
    for e in client.university.exams.find():
        exams.append(e)
    return {'exams': exams}


if __name__ == "__main__":
    for e in getExams()['exams']:
        print(e)
