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

# CLASS 명
HOMEBUTTON = "home_team_btn"
AWAYBUTTON = "away_team_btn"

# 기타 변수
FILEROUTE = '/Users/admin/chromedriver'
DATAFRAME = ['Date', 'Day', 'Stadium', 'Team', 'Position', 'Back_Number', 'Name', 'Substitute', 'Goal', 'Assist', 'Shoot', 'Foul', 'Yellow_Card', 'Sending_Off', 'Corner_Kick', 'Off-side']
FILENAME = "Naver_PlayerStat"
league_str = "Amatch"

def setDriver(url, driver):
    driver.get(url)
    page = driver.page_source
    soup = bs(page, 'html.parser')  # Selenium driver로 가져온 페이지를 읽기 위해 BeautifulSoup사용하기
    return soup

def setBasicInfo():
    league_url = URL + CATEGORY
    driver = webdriver.Chrome(FILEROUTE)
    schedule_soup = setDriver(league_url, driver)
    recording_link = schedule_soup.select('div.inner > a')  # 경기 기록 버튼 bs로 찾기
    each_game_stat_list = getData(recording_link, driver)  # getData 함수를 통해 crawling
    driver.close()
    return each_game_stat_list

def getStat(BUTTON, driver, recording_soup, d_day, day, stadium):
    stat_list = []
    driver.find_element_by_css_selector('#player_stats_btn').click()
    team_name = recording_soup.find('a', id=BUTTON).span.get_text()
    driver.find_element_by_css_selector('#' + BUTTON).click()
    # Home/Away 버튼을 클릭함으로써 page_source가 달라졌기 때문에 html.parser를 다시 불러와서 page source를 읽음.
    btn_change_soup = bs(driver.page_source, 'html.parser')
    player_record_box = btn_change_soup.find('tbody', id='player_record_box').findAll('tr')
    for each_player in range(len(player_record_box)):
        raw = player_record_box[each_player].findAll('td')
        # 교체된 선수인 경우 선수 이름 옆에 OUT ICON이 함께 크롤링 되기 때문에 확인
        is_exist_exchange = player_record_box[each_player].find('td', class_='name').span
        raw_data = []
        raw_data.append(d_day)  # 1. Date
        raw_data.append(day)  # 2. Day
        raw_data.append(stadium)  # 3. Stadium
        raw_data.append(team_name)  # 4. Team
        # 5. Position ~ # 16. Off-Side
        for each_column in range(len(raw)):
            if each_column == 2 and is_exist_exchange:
                out_signal = player_record_box[each_player].find('td', class_='name').em.get_text()
                raw_data.append(raw[each_column].get_text().split(out_signal)[0])
            else:
                raw_data.append(raw[each_column].get_text())
        stat_list.append(raw_data)
    return stat_list

def getData(recording_link, driver):
    each_month_stat_list = []
    for j in tqdm(range(len(recording_link))):
        if recording_link[j].get_text() == '경기기록' and recording_link[j].get('href'):
            game_url = recording_link[j].get('href')
            recording_soup = setDriver(game_url, driver)
            get_date_info = recording_soup.find('p', class_='d_day').get_text()
            month = get_date_info.split('.')[0]
            date = get_date_info.split('.')[1].split('(')[0]
            day = get_date_info.split('.')[1].split('(')[1].split(')')[0]
            d_day = datetime.date(int(year), int(month), int(date))
            stadium = get_date_info.split(') ')[1]
            home_team_stat = getStat(HOMEBUTTON, driver, recording_soup, d_day, day, stadium)
            away_team_stat = getStat(AWAYBUTTON, driver, recording_soup, d_day, day, stadium)
            team_stat = home_team_stat + away_team_stat
            each_month_stat_list.extend(team_stat)
    return each_month_stat_list

def checkPlyerBackNumber(get_squad_name):
    player_list = []
    for l in range(len(get_squad_name)):
        squad_data = get_squad_name[l].get_text()
        player_list.append(squad_data)
    return player_list

def crawlAmatchPlayerStat():
    each_game_stat_list = setBasicInfo()
    NaverCommon.saveAsCsv(each_game_stat_list, league_str, DATAFRAME, FILENAME)

if __name__ == "__main__":
    crawlAmatchPlayerStat()