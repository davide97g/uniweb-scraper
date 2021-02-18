# api.py
# ? here are contained all the API exposed by the webapp
import flask
from flask_cors import CORS, cross_origin


if __name__ == "__main__":
    from database import getExams, saveExams
    from scraper import scrapeExams
else:
    from app.database import getExams, saveExams
    from app.scraper import scrapeExams

app = flask.Flask(__name__)
app.config["DEBUG"] = True
app.config['CORS_HEADERS'] = 'Content-Type'

CORS(app)


@app.route('/exams/update', methods=['POST'])
@cross_origin()
def updateExams():
    exams = scrapeExams()
    return saveExams(exams)


@app.route('/exams', methods=['GET'])
@cross_origin()
def exams():
    return getExams()


if __name__ == "__main__":
    app.run()
