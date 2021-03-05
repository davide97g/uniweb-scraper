# database.py
from pymongo import MongoClient
from dotenv import load_dotenv
from progress.bar import ChargingBar
import os

load_dotenv()

client = MongoClient(os.environ.get("MONGODB_CONNECTION_STRING"))

# database: university
# collection: exams

# ? exams registered


def saveExamsRegistered(exams):
    bar = ChargingBar('Saving registered exams', max=len(exams))
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
    return {'message': 'Registered exams saved correctly.', 'data': exams}


def getExamsRegistered():
    exams = []
    for e in client.university.exams.find():
        exams.append(e)
    return {'exams': exams}

# ? exams results


def saveExamsResults(exams):
    bar = ChargingBar('Saving exams results', max=len(exams))
    for exam in exams:
        # todo: check different data to save
        client.university.exams_results.update_one({"_id": exam['id']},
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
    return {'message': 'Exams results saved correctly.', 'data': exams}


def getExamsResults():
    exams = []
    for e in client.university.exams_results.find():
        exams.append(e)
    return {'exams': exams}


if __name__ == "__main__":
    for e in getExamsRegistered()['exams']:
        print(e)
