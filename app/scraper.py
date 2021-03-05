# scraper.py
import os
import time
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv

if __name__ == "__main__":
    from database import saveExamsRegistered
    from database import saveExamsResults

# load environment variables
load_dotenv()

uniweb_username = os.environ.get("UNIWEB_USERNAME")
uniweb_password = os.environ.get("UNIWEB_PASSWORD")

# ? driver initialization
chrome_options = webdriver.ChromeOptions()
chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("window-size=1980,960")


if __name__ == "__main__":
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(
        executable_path="../driver/chromedriver", options=chrome_options)
else:
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(executable_path=os.environ.get(
        "CHROMEDRIVER_PATH"), options=chrome_options)

    # implicit wait
driver.implicitly_wait(10)  # seconds


def login():
    print("login...")
    driver.find_element_by_id("j_username_js").send_keys(uniweb_username)
    driver.find_element_by_id("password").send_keys(uniweb_password)
    driver.find_element_by_id("radio2").click()
    driver.find_element_by_id("login_button_js").click()


def career_choice(limit=10):
    # ? choice
    career_button = None  # crude initialization
    test = 0
    while not career_button and test < limit:
        career_choice_table = driver.find_element_by_id(
            "gu_table_sceltacarriera")
        if career_choice_table:
            career_links = career_choice_table.find_elements_by_tag_name("a")
            if career_links and len(career_links) > 0:
                career_button = career_links[0]  # take the first link
        time.sleep(1)
        test += 1
        print(f"{test} attempts to choose career")

    if not career_button or test == limit:
        print("error: career choice failed")
        return {'error': 'career choice failed.'}
    else:
        career_button.click()
        return {'success': 'career choice done.'}

# https://shibidp.cca.unipd.it/idp/profile/SAML2/Redirect/SSO?execution=e1s2


def extractRawDataExamsRegistered(limit=10):
    driver.get(
        "https://uniweb.unipd.it/auth/studente/Libretto/LibrettoHome.do?menu_opened_cod=menu_link-navbox_studenti_Home")

    # ? wait to be in the right page
    # while "Libretto" not in driver.find_element_by_tag_name("body").text:
    #     print("still not in Libretto online page...")
    #     time.sleep(1)
    #     driver.get(
    #         "https://uniweb.unipd.it/auth/studente/Libretto/LibrettoHome.do?menu_opened_cod=menu_link-navbox_studenti_Home")
    #     print(driver.find_element_by_tag_name("body").text)

    # ? get raw data for exams
    test = 0
    raw_exams = None  # crude initialization
    while not raw_exams and test < limit:
        tableLibretto = driver.find_element_by_id("tableLibretto")
        if tableLibretto:
            raw_exams = tableLibretto.text
        time.sleep(1)
        test += 1
        print(f"{test} attempts to get raw exams data")

    if not raw_exams or test == limit:
        return {"error": "exam data scraping failed"}

    # ? scraped raw data exams
    raw_data_exams = raw_exams.split("\n")
    if raw_data_exams:
        return {
            'success': "Raw data registered exams scraped.",
            'data': raw_data_exams}
    else:
        return {'error': 'Raw data scraping failed.'}


def parseExamsRegisteredData(exams_data):
    print("parsing exams data")
    exams_list = []
    columns = ['id', 'name', 'year', 'cfu', 'frequency', 'mark', 'date']
    for i in range(8, len(exams_data[8:]), 2):
        exam_id, exam_name = exams_data[i].split("-")
        exam_id = exam_id.replace(" ", "")
        exam_name = exam_name.lstrip(" ")
        exam_data = exams_data[i+1].split(" ")
        exam_data = [x for x in exam_data if x != '-']
        exam_year = exam_data[0]
        exam_cfu = exam_data[1]
        exam_frequency = exam_data[2]
        if len(exam_data) > 3:
            exam_mark = exam_data[3]
        else:
            exam_mark = ''
        if len(exam_data) == 5:
            exam_date = exam_data[4]
        else:
            exam_date = ''
        exams_list.append([exam_id, exam_name, exam_year, exam_cfu,
                           exam_frequency, exam_mark, exam_date])

    exams = []
    for e in exams_list:
        sample = {}
        for i in range(len(columns)):
            sample[columns[i]] = e[i]
        exams.append(sample)

    return exams


def extractRawDataExamsResults(limit=10):
    driver.get(
        "https://uniweb.unipd.it/auth/studente/Appelli/BachecaEsiti.do?menu_opened_cod=menu_link-navbox_studenti_Home")
    tables = driver.find_elements_by_tag_name("table")
    if tables and len(tables) == 2:
        # choose the table with less text
        table = tables[0]
        if len(tables[0].text) > len(tables[1].text):
            table = tables[1]
        return {'success': "Extracted raw data exams results.", 'data': table.text.split("\n")}
    else:
        return {'error': "Exams results => table not found."}


def parseExamsResultsData(exams_data):
    exams = []
    print(exams_data)
    print(len(exams_data))
    print(int(len(exams_data)/5))
    for i in range(int(len(exams_data)/5)):
        name, code, _ = exams_data[i].split(" - ")
        date = exams_data[i+2].split(" ")[0]
        hour = exams_data[i+2].split(" ")[1]
        date_last_reject = exams_data[i+3]
        mark = exams_data[i+4]
        exams.append({
            'name': name,
            'code': code.replace("[", "").replace("]", ""),
            'date': date,
            'hour': hour,
            'date_last_reject': date_last_reject,
            'mark': mark
        })
    return {'exams': exams}


def scrapeExams(input_password, registered=True, limit=10):
    if input_password != uniweb_password:
        return {'error': 'Password not correct.'}
    else:
        print("Password is correct")
    # go to login
    driver.get(
        "https://uniweb.unipd.it/Home.do")

    driver.find_element_by_id("hamburger").click()
    time.sleep(0.1)
    driver.find_element_by_id("menu_link-navbox_account_auth/Logon").click()
    time.sleep(0.5)
    test = 0
    while "shibidp" in driver.current_url and test < limit:
        login()
        time.sleep(1)
        test += 1
        print(f"{test} attempts to login")

    if "shibidp" in driver.current_url or test == limit:
        print("error: login failed")
        return {'error': 'login failed'}

    print("logged")

    # ? choice
    res = career_choice(limit)
    if 'success' in res:
        print(res.get("success"))
    elif 'error' in res:
        return res
    else:
        return {"error": "An error occurred during the career choice."}

    time.sleep(1)

    if registered:

        res = extractRawDataExamsRegistered(limit)

        driver.quit()

        if 'error' in res:
            return res
        elif 'success' in res:
            print(res.get("success"))

        raw_data_exams = res.get("data")

        exams = parseExamsRegisteredData(raw_data_exams)
        if not exams:
            print("error: parsing failed")
            return {'error': 'parsing failed'}
        else:
            print("parsing complete")
            return {'exams': exams}
    else:

        res = extractRawDataExamsResults(limit)

        driver.quit()

        if 'error' in res:
            return res
        elif 'success' in res:
            return parseExamsResultsData(res.get("data"))
        else:
            return {"error": "An error occurred while scraping exams results."}


# ? local tests
if __name__ == "__main__":
    registered = False
    res = scrapeExams(uniweb_password, registered)
    if "exams" in res:
        exams = res.get("exams")
        if len(exams) > 0:
            print(f"Downloaded {len(exams)} exams")
            print(exams)
            if registered:
                print(saveExamsRegistered(exams))
            else:
                print(saveExamsResults(exams))
    elif "error" in res:
        print(res.get("error"))
    else:
        print("An error occurred.")
