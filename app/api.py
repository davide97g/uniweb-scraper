# api.py
import flask
from flask_cors import CORS, cross_origin
from app.database import getExams, saveExams
from app.scraper import scrapeExamsList

app = flask.Flask(__name__)
app.config["DEBUG"] = True
app.config['CORS_HEADERS'] = 'Content-Type'

CORS(app)


@app.route('/exams/update', methods=['POST'])
@cross_origin()
def updateExams():
    exams = scrapeExamsList()
    return saveExams(exams)


@app.route('/exams', methods=['GET'])
@cross_origin()
def exams():
    return getExams()


if __name__ == "__main__":
    app.run()
