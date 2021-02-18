

def scrapeExams():
    print("Scraping exams...")
    mock_exam = {
        "id": "002",
        "name": "Business Economics and Financial Data",
        "year": "2020/2021",
        "cfu": 6,
        "frequency": "",
        "mark": 26,
        "date": "21/01/2021"
    }
    return [mock_exam]


# ? local tests
if __name__ == "__main__":
    from database import saveExams
    exams = scrapeExams()
    saveExams(exams)
