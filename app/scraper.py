# scraper.py
import os
import time
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv

if __name__ == "__main__":
    from database import saveExams

# load environment variables
load_dotenv()

uniweb_username = os.environ.get("UNIWEB_USERNAME")
uniweb_password = os.environ.get("UNIWEB_PASSWORD")

# ? driver initialization
chrome_options = webdriver.ChromeOptions()
chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")


if __name__ == "__main__":
    # chrome_options.add_argument("--headless")
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

# https://shibidp.cca.unipd.it/idp/profile/SAML2/Redirect/SSO?execution=e1s2


def scrapeExamsList(limit=10):

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
        return {'error': 'career choice failed'}

    # choice done
    career_button.click()
    print("choice done")
    time.sleep(1)

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
        print("error: exam data scraping failed")
        return {"error": "exam data scraping failed"}

    # ? scraped raw data exams
    print("raw data exams scraped")
    raw_data_exams = raw_exams.split("\n")
    print(raw_data_exams)

    driver.quit()

    if not raw_data_exams:
        print("error: scraping failed")
        return {'error': 'scraping failed'}
    else:
        exams = parseExamsData(raw_data_exams)
        if not exams:
            print("error: parsing failed")
            return {'error': 'parsing failed'}
        else:
            print("parsing complete")
            return {'exams': exams}

# ? mock data
# exams_data = ['Attività didattica', 'Anno di corso', 'CFU', 'Stato', 'Frequenza', 'Voto - Data Esame', 'Ric.', 'Prove Appelli', 'SCP7079405 - BIOINFORMATICS', '0 6  ', 'SCP8084903 - INTRODUCTION TO MOLECULAR BIOLOGY', '0 6  ', 'SCP7079257 - ALGORITHMIC METHODS AND MACHINE LEARNING', '1 12 2019/2020 30 - 24/07/2020', 'SCP7079297 - BIG DATA COMPUTING', '1 6 2019/2020', 'SCP7079317 - BIOINFORMATICS AND COMPUTATIONAL BIOLOGY', '1 6 2019/2020', 'SCP7079219 - COGNITIVE, BEHAVIORAL AND SOCIAL DATA', '1 6 2019/2020 30 - 27/01/2020', 'SCP9087561 - DEEP LEARNING', '1 6 2019/2020', 'SCP7078720 - FUNDAMENTALS OF INFORMATION SYSTEMS',
#               '1 12 2019/2020 30L - 10/09/2020', 'SCP7079397 - HUMAN DATA ANALYTICS', '1 6 2019/2020', 'SCP7079229 - OPTIMIZATION FOR DATA SCIENCE', '1 6 2019/2020', 'SCP7079226 - STATISTICAL LEARNING (C.I.)', '1 12 2019/2020', 'SCP7079197 - STOCHASTIC METHODS', '1 6 2019/2020', 'SCP7079278 - STRUCTURAL BIOINFORMATICS', '1 6 2019/2020', 'SCP9087563 - VISION AND COGNITIVE SERVICES', '1 6 2019/2020', 'SCP7079337 - BIOLOGICAL DATA', '2 6 2020/2021', 'SCP7079231 - BUSINESS ECONOMIC AND FINANCIAL DATA', '2 6 2020/2021', 'SCP7079319 - FINAL EXAMINATION', '2 15 2020/2021', 'SCP7079232 - STAGE', '2 15 2020/2021']


def parseExamsData(exams_data):
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


# ? local tests
if __name__ == "__main__":
    res = scrapeExamsList()
    if res.get("exams") is not None:
        exams = res.get("exams")
        if len(exams) > 0:
            print(f"Downloaded {len(exams)} exams")
            print(exams)
            # saveExams(exams)
    else:
        print("No exams downloaded.")
