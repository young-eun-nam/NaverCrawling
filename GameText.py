from bs4 import BeautifulSoup as bs
from tqdm import *
from selenium import webdriver
import NaverCommon

# URL 변수
URL = "https://sports.news.naver.com/kfootball/schedule/index.nhn?"
CATEGORY = "category="
YEAR = "&year=2018"
MONTH = "&month="

# 기타 변수
CONSOLEGUIDE = "Input league number(league_num 1:K1, 2:K2):  "
FILEROUTE = '/Users/admin/chromedriver'
DATAFRAME = ['Home_Team', 'Away_Team', 'Minute', 'Second', 'Team', 'Back_Number', 'Name', 'Event']
FILENAME = "Naver_TextBroadcast"

def setDriver(url, driver):
    driver. get(url)
    page = driver.page_source
    soup = bs(page, 'html.parser')  # Selenium driver로 가져온 페이지를 읽기 위해 BeautifulSoup사용하기
    return soup

def setBasicInfo(league_str):
    league_url = URL + CATEGORY + league_str
    driver = webdriver.Chrome(FILEROUTE)
    schedule_soup = setDriver(league_url, driver)
    month_list = schedule_soup.findAll('span', class_='month')  # 경기가 있었던 달 crawl
    result = []
    for i in range(len(month_list)):
        month = month_list[i].get_text().split('월')[0].zfill(2)
        month_url = league_url + YEAR + MONTH + month
        each_month_soup = setDriver(month_url, driver)
        recording_link = each_month_soup.select('div.inner > a')    # 경기 기록 버튼 bs로 찾기
        each_month_event_list = getData(recording_link, driver)     # getData 함수를 통해 crawling
        result.extend(each_month_event_list)
    driver.close()
    return result

def getData(recording_link, driver):
    each_month_event_list = []
    for j in tqdm(range(len(recording_link))):
        if recording_link[j].get_text() == '경기기록' and recording_link[j].get('href'):
            game_url = recording_link[j].get('href')
            recording_soup = setDriver(game_url, driver)
            text_broadcast = recording_soup.select('ul.lst_sms > li')
            event_list = []
            for k in reversed(range(len(text_broadcast))):
                raw_data = []
                get_class_name = text_broadcast[k].get('class')
                get_time = recording_soup.findAll('strong', class_='time')[k].get_text().split(":")
                get_team_name = recording_soup.findAll('strong', class_='team_name')

                # 문자 중계 중 class_name의 길이가 2인 경우에만 주요 event로 Strong text - Strong text인 문자중계만 crawling
                if (len(get_class_name)) == 2:
                    minute = get_time[0]
                    second = get_time[1]
                    team = recording_soup.findAll('div', class_='sms')[k].find('strong').get_text().split(' ㅣ ')[0]
                    name = recording_soup.findAll('div', class_='sms')[k].find('strong').get_text().split(' ㅣ ')[1].split(' ')[0]
                    event = recording_soup.findAll('div', class_='sms')[k].find('strong').get_text().split(' ㅣ ')[1].split(' ')[1]
                    get_squad_name = recording_soup.findAll('tbody', id='squad_list')[0].findAll('td', class_='name')
                    player_list = checkPlyerBackNumber(get_squad_name)
                    # event가 교체인 경우에만 Strong text 외에 일반 text도 crawling하여 교체 상대를 알 수 있게 함.
                    if event == "교체":
                        IN = recording_soup.findAll('div', class_='sms')[k].get_text().split('교체')[1].split(' 나가고 ')[1].split(' 들어옵니다')[0]
                        event = event + " with " + IN
                    else:
                        pass
                    raw_data.append(get_team_name[0].get_text())                                        # 1. Home_Team
                    raw_data.append(get_team_name[1].get_text())                                        # 2. Away_Team
                    raw_data.append(minute)                                                             # 3. Minute
                    raw_data.append(second)                                                             # 4. Second
                    raw_data.append(team)                                                               # 5. Team
                    if name in player_list:
                        player_list_index = player_list.index(name)
                        raw_data.append(get_squad_name[player_list_index].previous_sibling.get_text())  # 6. Back_Number
                    raw_data.append(name)                                                               # 7. Name
                    raw_data.append(event)                                                              # 8. Event
                    event_list.append(raw_data)
            each_month_event_list.extend(event_list)
    return each_month_event_list

def checkPlyerBackNumber(get_squad_name):
    player_list = []
    for l in range(len(get_squad_name)):
        squad_data = get_squad_name[l].get_text()
        player_list.append(squad_data)
    return player_list

def crawlNaverTextBroadcast():
    while True:
        league_num = input(CONSOLEGUIDE)
        if league_num in ["1"]:
            league_str = "kleague"
        elif league_num in ["2"]:
            league_str = "kleague" + league_num
        else:
            print(CONSOLEGUIDE)
            continue
        result = setBasicInfo(league_str)
        NaverCommon.saveAsCsv(result, league_str, DATAFRAME, FILENAME)

if __name__ == "__main__":
    crawlNaverTextBroadcast()