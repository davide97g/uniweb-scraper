# api.py
import flask
from flask import request
from flask_cors import CORS, cross_origin
from app.database import getExamsRegistered, getExamsResults, saveExamsRegistered, saveExamsResults
from app.scraper import scrapeExams

app = flask.Flask(__name__)
app.config["DEBUG"] = True
app.config['CORS_HEADERS'] = 'Content-Type'

CORS(app)


@app.route('/exams/registered/update', methods=['POST'])
@cross_origin()
def updateExamsRegistered():
    uniweb_password = request.json.get("uniweb_password")
    res = scrapeExams(uniweb_password, True)
    if 'exams' in res:
        return saveExamsRegistered(res.get("exams"))
    elif 'error' in res:
        return res['error']
    else:
        return "An error occured."


@app.route('/exams/registered', methods=['GET'])
@cross_origin()
def examsRegistered():
    return getExamsRegistered()


@app.route('/exams/results/update', methods=['POST'])
@cross_origin()
def updateExamsResults():
    uniweb_password = request.json.get("uniweb_password")
    res = scrapeExams(uniweb_password, False)
    if 'exams' in res:
        return saveExamsResults(res.get("exams"))
    elif 'error' in res:
        return res['error']
    else:
        return "An error occured."


@app.route('/exams/results', methods=['GET'])
@cross_origin()
def examsResults():
    return getExamsResults()


if __name__ == "__main__":
    app.run()
