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
YEARURL = "&year="
YEAR = YEARURL + year
MONTH = "&month="

# CLASS 명
HOMEBUTTON = "home_team_btn"
AWAYBUTTON = "away_team_btn"

# 기타 변수
FILEROUTE = '/Users/admin/chromedriver'
STATDATAFRAME = ['Date', 'Day', 'Stadium', 'Team', 'Position', 'Back_Number', 'Name', 'Substitute', 'Goal', 'Assist', 'Shoot', 'Foul', 'Yellow_Card', 'Sending_Off', 'Corner_Kick', 'Off-side']
TEXTDATAFRAME = ['Date', 'Day', 'Stadium', 'Home_Team', 'Away_Team', 'Minute', 'Second', 'Team', 'Back_Number', 'Name', 'Event', 'In_Player_Back_Number', 'In_Player_Name']
STATFILENAME = "Naver_PlayerStat"
TEXTFILENAME = "Naver_TextBroadcast"
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
    each_game_stat_list, each_game_event_list = getData(recording_link, driver)  # getData 함수를 통해 crawling
    driver.close()
    return each_game_stat_list, each_game_event_list

def getStat(BUTTON, driver, recording_soup, d_day, day, stadium):
    stat_list = []
    driver.find_element_by_css_selector('#player_stats_btn').click()
    team_name = recording_soup.find('a', id=BUTTON).span.get_text()
    driver.find_element_by_css_selector('#' + BUTTON).click()
    # Home/Away 버튼을 클릭함으로써 page_source가 달라졌기 때문에 html.parser를 다시 불러와서 page source를 읽음.
    btn_change_soup = bs(driver.page_source, 'html.parser')
    player_record_box = btn_change_soup.find('tbody', id='player_record_box').findAll('tr')
    back_number_list = []
    squad_name_list = []
    exchange_list = []
    for each_player in range(len(player_record_box)):
        raw = player_record_box[each_player].findAll('td')
        # 교체된 선수인 경우 선수 이름 옆에 OUT ICON이 함께 크롤링 되기 때문에 확인
        is_exist_exchange = player_record_box[each_player].find('td', class_='name').span
        raw_data = []
        raw_data.append(d_day)      # 1. Date
        raw_data.append(day)        # 2. Day
        raw_data.append(stadium)    # 3. Stadium
        raw_data.append(team_name)  # 4. Team
        # 5. Position ~ # 16. Off-Side
        for each_column in range(len(raw)):
            if each_column == 1:
                back_number_list.append(raw[each_column].get_text())
                raw_data.append(raw[each_column].get_text())
            elif each_column == 2:
                if is_exist_exchange:
                    out_signal = player_record_box[each_player].find('td', class_='name').em.get_text()
                    raw_data.append(raw[each_column].get_text().split(out_signal)[0])
                    squad_name_list.append(raw[each_column].get_text().split(out_signal)[0])
                else:
                    raw_data.append(raw[each_column].get_text())
                    squad_name_list.append(raw[each_column].get_text())
            elif each_column == 3:
                raw_data.append(raw[each_column].get_text())
                exchange_list.append(raw[each_column].get_text())
            else:
                raw_data.append(raw[each_column].get_text())
        stat_list.append(raw_data)
    return stat_list, back_number_list, squad_name_list, exchange_list

def getGameText(recording_soup, d_day, day, stadium, back_number_list, squad_name_list, exchange_list):
    text_broadcast = recording_soup.select('ul.lst_sms > li')
    event_list = []
    for j in reversed(range(len(text_broadcast))):
        raw_data = []
        get_class_name = text_broadcast[j].get('class')
        get_time = recording_soup.findAll('strong', class_='time')[j].get_text().split(":")
        get_team_name = recording_soup.findAll('strong', class_='team_name')

        # 문자 중계 중 class_name의 길이가 2인 경우에만 주요 event로 Strong text - Strong text인 문자중계만 crawling
        if (len(get_class_name)) == 2:
            minute = get_time[0]
            second = get_time[1]
            team = recording_soup.findAll('div', class_='sms')[j].find('strong').get_text().split(' ㅣ ')[0]
            after_bar = recording_soup.findAll('div', class_='sms')[j].find('strong').get_text().split(' ㅣ ')[1].split(' ')
            name = " ".join(after_bar[0:len(after_bar) - 1])
            event = after_bar[len(after_bar) - 1]

            raw_data.append(d_day)                                      # 1. Date
            raw_data.append(day)                                        # 2. Day
            raw_data.append(stadium)                                    # 3. Stadium
            raw_data.append(get_team_name[0].get_text())                # 4. Home_Team
            raw_data.append(get_team_name[1].get_text())                # 5. Away_Team
            raw_data.append(minute)                                     # 6. Minute
            raw_data.append(second)                                     # 7. Second
            raw_data.append(team)                                       # 8. Team
            if name in squad_name_list:
                player_list_index = squad_name_list.index(name)
                raw_data.append(back_number_list[player_list_index])    # 9. Back_Number
            raw_data.append(name)                                       # 10. Name
            raw_data.append(event)                                      # 11. Event
            if event == "교체":
                if name in squad_name_list:
                    player_index = squad_name_list.index(name)
                    if exchange_list[player_index] in squad_name_list:
                        exchange_index = squad_name_list.index(exchange_list[player_index])
                        raw_data.append(back_number_list[exchange_index])   # 12. In_Player_Back_Number
                        raw_data.append(squad_name_list[exchange_index])    # 13. In_Player_Name
            event_list.append(raw_data)
    return event_list

def getData(recording_link, driver):
    each_month_stat_list = []
    each_game_event_list = []
    for i in tqdm(range(len(recording_link))):
        if recording_link[i].get_text() == '경기기록' and recording_link[i].get('href'):
            game_url = recording_link[i].get('href')
            recording_soup = setDriver(game_url, driver)
            get_date_info = recording_soup.find('p', class_='d_day').get_text()
            month = get_date_info.split('.')[0]
            date = get_date_info.split('.')[1].split('(')[0]
            day = get_date_info.split('.')[1].split('(')[1].split(')')[0]
            d_day = datetime.date(int(year), int(month), int(date))
            stadium = get_date_info.split(') ')[1]
            home_team_stat, home_back_number_list, home_squad_name_list, home_exchange_list = getStat(HOMEBUTTON, driver, recording_soup, d_day, day, stadium)
            away_team_stat, away_back_number_list, away_squad_name_list, away_exchange_list = getStat(AWAYBUTTON, driver, recording_soup, d_day, day, stadium)
            back_number_list = mergeTwoLists(home_back_number_list, away_back_number_list)
            squad_name_list = mergeTwoLists(home_squad_name_list, away_squad_name_list)
            exchange_list = mergeTwoLists(home_exchange_list, away_exchange_list)
            team_stat = mergeTwoLists(home_team_stat, away_team_stat)
            event_list = getGameText(recording_soup, d_day, day, stadium, back_number_list, squad_name_list, exchange_list)
            each_month_stat_list.extend(team_stat)
            each_game_event_list.extend(event_list)
    return each_month_stat_list, each_game_event_list

def checkPlyerBackNumber(get_squad_name):
    player_list = []
    for l in range(len(get_squad_name)):
        squad_data = get_squad_name[l].get_text()
        player_list.append(squad_data)
    return player_list

def mergeTwoLists(list_one, list_two):
    merge_list = list_one + list_two
    return merge_list

def crawlAmatch():
    each_game_stat_list, each_game_event_list = setBasicInfo()
    NaverCommon.saveAsCsv(each_game_stat_list, league_str, STATDATAFRAME, STATFILENAME)
    NaverCommon.saveAsCsv(each_game_event_list, league_str, TEXTDATAFRAME, TEXTFILENAME)

if __name__ == "__main__":
    crawlAmatch()