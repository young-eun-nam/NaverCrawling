from bs4 import BeautifulSoup as bs
from tqdm import *
from selenium import webdriver
import datetime
import NaverCommon

# URL 변수
year = "2018"
URL = "https://sports.news.naver.com/kfootball/schedule/index.nhn?"
GAMEURL = "https://sports.news.naver.com/gameCenter/textRelayFootball.nhn?"
CATEGORY = "category=amatch"
YEARUIL = "&year="
YEAR = YEARUIL + year
MONTH = "&month="

# 기타 변수
FILEROUTE = '/Users/admin/chromedriver'
DATAFRAME = ['Date', 'Day', 'Stadium', 'Home_Team', 'Away_Team', 'Minute', 'Second', 'Team', 'Back_Number', 'Name', 'Event']
FILENAME = "Naver_TextBroadcast"
league_str = "Amatch"

def setDriver(url, driver):
    driver. get(url)
    page = driver.page_source
    soup = bs(page, 'html.parser')  # Selenium driver로 가져온 페이지를 읽기 위해 BeautifulSoup사용하기
    return soup

def setBasicInfo():
    league_url = URL + CATEGORY
    driver = webdriver.Chrome(FILEROUTE)
    schedule_soup = setDriver(league_url, driver)
    recording_link = schedule_soup.select('div.inner > a')    # 경기 기록 버튼 bs로 찾기
    each_game_event_list = getData(recording_link, driver)     # getData 함수를 통해 crawling
    driver.close()
    return each_game_event_list

def getData(recording_link, driver):
    each_game_event_list = []
    for i in tqdm(range(len(recording_link))):
        if recording_link[i].get_text() == '경기기록' and recording_link[i].get('href'):
            game_url = recording_link[i].get('href')
            recording_soup = setDriver(game_url, driver)
            text_broadcast = recording_soup.select('ul.lst_sms > li')
            event_list = []
            for j in reversed(range(len(text_broadcast))):
                raw_data = []
                get_class_name = text_broadcast[j].get('class')
                get_time = recording_soup.findAll('strong', class_='time')[j].get_text().split(":")
                get_team_name = recording_soup.findAll('strong', class_='team_name')
                get_date_info = recording_soup.find('p', class_='d_day').get_text()
                month = get_date_info.split('.')[0]
                date = get_date_info.split('.')[1].split('(')[0]
                day = get_date_info.split('.')[1].split('(')[1].split(')')[0]
                d_day = datetime.date(int(year), int(month), int(date))
                stadium = get_date_info.split(') ')[1]

                # 문자 중계 중 class_name의 길이가 2인 경우에만 주요 event로 Strong text - Strong text인 문자중계만 crawling
                if (len(get_class_name)) == 2:
                    minute = get_time[0]
                    second = get_time[1]
                    team = recording_soup.findAll('div', class_='sms')[j].find('strong').get_text().split(' ㅣ ')[0]
                    after_bar = recording_soup.findAll('div', class_='sms')[j].find('strong').get_text().split(' ㅣ ')[1].split(' ')
                    name = " ".join(after_bar[0:len(after_bar)-1])
                    event = after_bar[len(after_bar)-1]
                    get_starting_name = recording_soup.findAll('tbody', id='starting_list')[0].findAll('td', class_='name')
                    get_reserve_name = recording_soup.findAll('tbody', id='reserve_list')[0].findAll('td', class_='name')
                    get_player_list = get_starting_name + get_reserve_name
                    squad_list = checkPlyerBackNumber(get_player_list)

                    raw_data.append(d_day)                                                                  # 1. Date
                    raw_data.append(day)                                                                    # 2. Day
                    raw_data.append(stadium)                                                                # 3. Stadium
                    raw_data.append(get_team_name[0].get_text())                                            # 4. Home_Team
                    raw_data.append(get_team_name[1].get_text())                                            # 5. Away_Team
                    raw_data.append(minute)                                                                 # 6. Minute
                    raw_data.append(second)                                                                 # 7. Second
                    raw_data.append(team)                                                                   # 8. Team
                    if name in squad_list:
                        player_list_index = squad_list.index(name)
                        raw_data.append(get_player_list[player_list_index].next_sibling.get_text())         # 9. Back_Number
                    # Amatch 대한민국 상대팀인 경우 squad list가 제공되지 않으므로 등번호 NULL값
                    elif team == get_team_name[1].get_text():
                        raw_data.append("")
                    raw_data.append(name)                                                                   # 10. Name
                    raw_data.append(event)                                                                  # 11. Event
                    event_list.append(raw_data)
            each_game_event_list.extend(event_list)
    return each_game_event_list

def checkPlyerBackNumber(get_player_list):
    player_list = []
    for k in range(len(get_player_list)):
        squad_data = get_player_list[k].get_text()
        player_list.append(squad_data)
    return player_list

def crawlNaverTextBroadcast():
    each_game_event_list = setBasicInfo()
    NaverCommon.saveAsCsv(each_game_event_list, league_str, DATAFRAME, FILENAME)

if __name__ == "__main__":
    crawlNaverTextBroadcast()