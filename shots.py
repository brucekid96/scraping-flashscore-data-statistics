from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
from pprint import pprint
from tabulate import tabulate



def initialize_driver():
    driver_options = webdriver.ChromeOptions()
    driver_options.add_experimental_option('prefs', {'profile.managed_default_content_settings.images': 2})
    driver_options.add_argument("--headless")
    driver = webdriver.Chrome(options=driver_options)
    return driver


def get_matches():
    driver = initialize_driver()
    driver.get('https://www.flashscore.com/football/england/premier-league/results')
    match_section = driver.find_element(By.CSS_SELECTOR, 'div.sportName.soccer')
    match_section_divs = match_section.find_elements(By.XPATH, './child::*')
    match_divs = [div for div in match_section_divs if 'g_' in div.get_attribute('id')]
    matches = [extract_match_data(div) for div in match_divs]
    driver.quit()
    return matches

def extract_match_data(match_div):    
    match_id = match_div.get_attribute('id')[4:]
    home_team = match_div.find_element(By.CSS_SELECTOR, 'div.event__participant.event__participant--home').get_attribute('innerText')
    away_team = match_div.find_element(By.CSS_SELECTOR, 'div.event__participant.event__participant--away').get_attribute('innerText')
    match_time = match_div.find_element(By.CSS_SELECTOR, 'div.event__time').get_attribute('innerText')

    return {
        'id': match_id,
        'home_team': home_team,
        'away_team': away_team,
        'time': match_time
    }

def get_match_stats(match_id):
    driver = initialize_driver()
    driver.get('https://www.flashscore.com/match/{}/#/match-summary/match-statistics/0'.format(match_id))
    
    stat_divs = driver.find_elements(By.CSS_SELECTOR, 'div.stat__row')
    stat_dict = {}
    extracted_stats = [extract_stat(stat) for stat in stat_divs]
    for stat in extracted_stats:
        stat_dict[stat['name']] = (stat['home_value'], stat['away_value'])
    driver.quit()
    return stat_dict

def extract_stat(stat_row_div):
    category_name = stat_row_div.find_element(By.CSS_SELECTOR, 'div.stat__categoryName').get_attribute('innerText')
    home_value = stat_row_div.find_element(By.CSS_SELECTOR, 'div.stat__homeValue').get_attribute('innerText')
    away_value = stat_row_div.find_element(By.CSS_SELECTOR, 'div.stat__awayValue').get_attribute('innerText')
    
    return {
        'name': category_name,
        'home_value': home_value,
        'away_value': away_value
    }

# def show_all_matches():
#     more_matches_link = driver.find_elements(By.CSS_SELECTOR, 'a.event__more.event__more--static')
#     while(len(more_matches_link) > 0):
#         driver.execute_script('arguments[0].click();', more_matches_link[0])
#         more_matches_link = driver.find_elements(By.CSS_SELECTOR, 'a.event__more.event__more--static')



def main():
    matches = get_matches()[:7]
    print('Matches')
    pprint(matches)
    
    summary_table = []
    summary_table_headers = ['Match ID', 'Time', 'Home Team', 'Away Team', 'Shots Winner', 'Shots Difference']

    for match in matches:
        match_stats = get_match_stats(match['id'])

        shots_difference = 0
        shots_winner = 'N/A'

        if 'Shots on Goal' in match_stats:
            shots_difference = int(match_stats['Shots on Goal'][0]) - int(match_stats['Shots on Goal'][1])
            shots_winner = match['home_team'] if shots_difference > 0 else match['away_team'] if shots_difference < 0 else '---'

        summary_line = [match['id'], match['time'], match['home_team'], match['away_team'], shots_winner, abs(shots_difference)]
        print(summary_line)
        summary_table.append(summary_line)

    print('\n\n\n\n\n')
    print(tabulate(summary_table, headers=summary_table_headers, tablefmt='double_grid'))
    print('\n\n\n')


main()

