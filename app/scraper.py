# https://shibidp.cca.unipd.it/idp/profile/SAML2/Redirect/SSO?execution=e1s2
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import os
import time
from dotenv import load_dotenv
if __name__ == "__main__":
    from database import saveExams
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


def scrapeExams():

    # go to login
    driver.get(
        "https://uniweb.unipd.it/Home.do")

    driver.find_element_by_id("hamburger").click()
    time.sleep(0.1)
    driver.find_element_by_id("menu_link-navbox_account_auth/Logon").click()

    driver.find_element_by_id("j_username_js").send_keys(uniweb_username)
    driver.find_element_by_id("password").send_keys(uniweb_password)
    driver.find_element_by_id("radio2").click()
    driver.find_element_by_id("login_button_js").click()

    driver.find_element_by_id("gu_toolbar_sceltacarriera").click()
    time.sleep(0.5)

    driver.get("https://uniweb.unipd.it/auth/studente/Libretto/LibrettoHome.do?menu_opened_cod=menu_link-navbox_studenti_Home")
    time.sleep(0.5)
    raw_exams = driver.find_element_by_id("tableLibretto").text
    raw_data_exams = raw_exams.split("\n")

    driver.quit()

    if not raw_data_exams:
        return {'error': 'Scraping failed'}
    else:
        exams = parseExamsData(raw_data_exams)
        return {'exams': exams}

# ? mock data
# exams_data = ['Attività didattica', 'Anno di corso', 'CFU', 'Stato', 'Frequenza', 'Voto - Data Esame', 'Ric.', 'Prove Appelli', 'SCP7079405 - BIOINFORMATICS', '0 6  ', 'SCP8084903 - INTRODUCTION TO MOLECULAR BIOLOGY', '0 6  ', 'SCP7079257 - ALGORITHMIC METHODS AND MACHINE LEARNING', '1 12 2019/2020 30 - 24/07/2020', 'SCP7079297 - BIG DATA COMPUTING', '1 6 2019/2020', 'SCP7079317 - BIOINFORMATICS AND COMPUTATIONAL BIOLOGY', '1 6 2019/2020', 'SCP7079219 - COGNITIVE, BEHAVIORAL AND SOCIAL DATA', '1 6 2019/2020 30 - 27/01/2020', 'SCP9087561 - DEEP LEARNING', '1 6 2019/2020', 'SCP7078720 - FUNDAMENTALS OF INFORMATION SYSTEMS',
#               '1 12 2019/2020 30L - 10/09/2020', 'SCP7079397 - HUMAN DATA ANALYTICS', '1 6 2019/2020', 'SCP7079229 - OPTIMIZATION FOR DATA SCIENCE', '1 6 2019/2020', 'SCP7079226 - STATISTICAL LEARNING (C.I.)', '1 12 2019/2020', 'SCP7079197 - STOCHASTIC METHODS', '1 6 2019/2020', 'SCP7079278 - STRUCTURAL BIOINFORMATICS', '1 6 2019/2020', 'SCP9087563 - VISION AND COGNITIVE SERVICES', '1 6 2019/2020', 'SCP7079337 - BIOLOGICAL DATA', '2 6 2020/2021', 'SCP7079231 - BUSINESS ECONOMIC AND FINANCIAL DATA', '2 6 2020/2021', 'SCP7079319 - FINAL EXAMINATION', '2 15 2020/2021', 'SCP7079232 - STAGE', '2 15 2020/2021']


def parseExamsData(exams_data):
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
    res = scrapeExams()
    if res.get("exams") is not None:
        exams = res.get("exams")
        if len(exams) > 0:
            print(f"Downloaded {len(exams)} exams")
            print(exams)
            saveExams(exams)
    else:
        print("No exams downloaded.")
