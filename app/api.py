# api.py
import flask
from flask import request
from flask_cors import CORS, cross_origin
from app.database import getExamsRegistered, getExamsResults, saveExams
from app.scraper import scrapeExamsRegistered, scrapeExamsResults

app = flask.Flask(__name__)
app.config["DEBUG"] = True
app.config['CORS_HEADERS'] = 'Content-Type'

CORS(app)


@app.route('/exams/registered/update', methods=['POST'])
@cross_origin()
def updateExamsRegistered():
    uniweb_password = request.json.get("uniweb_password")
    res = scrapeExamsRegistered(uniweb_password)
    if 'exams' in res:
        return saveExams(exams)
    elif 'error' in res:
        return res['error']
    else:
        return "An error occured."


@app.route('/exams/registered', methods=['GET'])
@cross_origin()
def exams():
    return getExamsRegistered()



@app.route('/exams/results/update', methods=['POST'])
@cross_origin()
def updateExamsResults():
    uniweb_password = request.json.get("uniweb_password")
    res = scrapeExamsResults(uniweb_password)
    if 'exams' in res:
        return saveExams(exams)
    elif 'error' in res:
        return res['error']
    else:
        return "An error occured."

@app.route('/exams/results', methods=['GET'])
@cross_origin()
def exams():
    return getExamsResults()


if __name__ == "__main__":
    app.run()
