from bs4 import BeautifulSoup as bs
from selenium import webdriver
import NaverCommon

# URL 변수
year = "2018"
URL = "https://sports.news.naver.com/kfootball/record/index.nhn?"
CATEGORY = "category="
YEARURL = "&year="
YEAR = YEARURL + year

# Class 변수
groupA = "splitGroupA_table"
groupB = "splitGroupB_table"
regular_round = "regularGroup_table"

# 기타 변수
CONSOLEGUIDE = "Input league number(league_num 1:K1, 2:K2):  "
FILEROUTE = '/Users/admin/chromedriver'
DATAFRAME = ['Ranking', 'Team', 'Played', 'Points', 'Won', 'Drawn', 'Loss', 'Goals_For', 'Goals_Against', 'Goals_Difference', 'Assist', 'Foul']
FILENAME = "Naver_Record"

def setDriver(url, driver):
    driver. get(url)
    page = driver.page_source
    soup = bs(page, 'html.parser')  # Selenium driver로 가져온 페이지를 읽기 위해 BeautifulSoup사용하기
    return soup

def getData(record_soup, class_name):
    record_box = record_soup.find('tbody', id=class_name).findAll('tr')
    matrix = []
    for raw_index in range(len(record_box)):
        ranking = record_box[raw_index].find('th').get_text()
        raw = record_box[raw_index].findAll('td')
        raw_data = []
        raw_data.append(ranking)
        for column_index in range(len(raw)):
            if column_index == 0:
                raw_data.append(raw[column_index].find('span').get_text())
            else:
                raw_data.append(raw[column_index].get_text())
        matrix.append(raw_data)
    return matrix

def setBasicInfo(league_num, league_str):
    record_url = URL + CATEGORY + league_str + YEAR

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    browser = webdriver.Chrome(chrome_options=chrome_options)

    driver = webdriver.Chrome()
    record_soup = setDriver(record_url, driver)
    if league_num in ["1"]:
        k1_groupA_result = getData(record_soup, groupA)
        k1_groupB_result = getData(record_soup, groupB)
        result = k1_groupA_result + k1_groupB_result
    elif league_num in ["2"]:
        result = getData(record_soup, regular_round)
    else:
        pass
    driver.close()
    return result

def crawlNaverRecord():
    while True:
        league_num = input(CONSOLEGUIDE)
        if league_num in ["1"]:
            league_str = "kleague"
        elif league_num in ["2"]:
            league_str = "kleague" + league_num
        else:
            print(CONSOLEGUIDE)
            continue
        result = setBasicInfo(league_num, league_str)
        NaverCommon.saveAsCsv(result, league_str, DATAFRAME, FILENAME)

if __name__ == "__main__":
    crawlNaverRecord()