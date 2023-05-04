import sqlite3
from selenium import webdriver 
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By

# Connect to the database
conn = sqlite3.connect('cache.db')
c = conn.cursor()


def format(arr):
    to_print = arr[0] + " / " + arr[1] + " / " + arr[2] + " / "  + arr[3] + " / " + arr[4] + " || vs || " + arr[5] + " / " + arr[6] + " / " + arr[7] + " / "  + arr[8] + " / " + arr[9]
    return(to_print)

def search(player):
    # start by defining the options 
    options = FirefoxOptions()
    options.add_argument("--headless")
    # normally, selenium waits for all resources to download 
    # we don't need it as the page also populated with the running javascript code. 
    options.page_load_strategy = 'none' 
    # pass the defined options and service objects to initialize the web driver 
    driver = webdriver.Firefox()
    driver.implicitly_wait(5)
    url = "https://www.factor.gg/champions-queue"
    driver.get(url) 
    team = []
    order = [0, 2, 4, 6, 8, 1, 3, 5, 7, 9]
    #matches = [['top1A', 'top1B', 'jg1A', 'jg1B', 'mid1A', 'mid1B', 'bot1A', 'bot1B', 'supp1A', 'supp1B'], ['top2A', 'top2B', 'jg2A', 'jg2B', 'mid2A', 'mid2B', 'bot2A', 'bot2B', 'supp2A', 'supp2B']]
    # matches = []
    matches = driver.find_elements(By.CSS_SELECTOR, "div[class*='py-2 bg-center bg-cover rounded-md bg-cqMatchcard']")
    for games in matches:
        players = games.find_elements(By.TAG_NAME, "p")
        team = [players[i].text for i in order]
        if player in games:
            team = [games[i] for i in order]
            return format(team)