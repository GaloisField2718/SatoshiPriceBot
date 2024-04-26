
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC

###########################################################
########            UTILS               ###################
###########################################################

from bs4 import BeautifulSoup
import requests as req

def parse_rune_name(rune):
    dot = '.'
    html_parse = '%E2%80%A2'
    spacer = '•'
    if rune.find(dot) != 0:
        rune = rune.replace(dot, spacer)
    elif rune.find(html_parse) != 0:
        rune = rune.replace(html_parse, spacer)
    return rune

def get_supply(rune):
    rune_name = parse_rune_name(rune)
    response = req.get(f'http://94.16.123.98:8080/rune/{rune_name}')
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')
    supply_text = soup.find('dt', string='supply').find_next_sibling('dd').text
    supply_float = float(supply_text.split()[0].replace(',', ''))
    return supply_float

def sat2btc(sats):
    return sats/(10**8)

def btc2sat(btc):
    return btc*10**8


############################################################

def fetch(rune):
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    
    rune_name = parse_rune_name(rune)
    driver.get(f'https://unisat.io/runes/market?tick={rune_name}')
    wait = WebDriverWait(driver, 10)
    
    floor_price_sats = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "price")))
    floor_price_sats = driver.find_element(By.XPATH, '//div[contains(@class, "price-line")]/span[contains(@class, "price")]')
    
    floor_runes = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "inscription-name  ")))
    floor_runes = driver.find_element(By.XPATH, '//div[contains(@class, "content display-domain white")]/div[contains(@class, "inscription-name  ")]')
    
    floor_usd = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "usd")))
    floor_usd = driver.find_element(By.XPATH, '//div[contains(@class, "price-line")]/span[contains(@class, "usd")]')
    
    xpath = "//*[@id='rc-tabs-0-panel-1']/div/div[1]/div[1]"
    floor_card_info = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
    floor_card_info = driver.find_element(By.XPATH, xpath)

    xpath_second = "//*[@id='rc-tabs-1-panel-1']/div/div[1]/div[2]"
    #second_card_info = wait.until(EC.presence_of_element_located((By.XPATH, xpath_second)))
    #second_card_info = driver.find_element(By.XPATH, xpath_second)
    
    #second_price_sats = driver.find_element(By.XPATH, '//*[@id="rc-tabs-1-panel-1"]/div/div[1]/div[2]/div[1]/div[3]/span[1]')
    #second_runes = driver.find_element(By.XPATH, '//*[@id="rc-tabs-1-panel-1"]/div/div[1]/div[2]/div[1]/div[2]')
    #second_usd = driver.find_element(By.XPATH, '//*[@id="rc-tabs-1-panel-1"]/div/div[1]/div[2]/div[1]/span')

    
    floor_price_sats = (floor_price_sats.text).replace(',', '')
    try:
        floor_price_sats = int(floor_price_sats)
    except ValueError:
        floor_price_sats = float(floor_price_sats)
    
    floor_price_btc = sat2btc(floor_price_sats)
    floor_runes = (floor_runes.text).replace(',','')
    try:
        floor_runes = int(floor_runes)
    except ValueError:
        floor_runes = float(floor_runes)

    floor_usd = floor_usd.text

    total_supply = get_supply(rune)

    floor_card = floor_card_info.text.split('\n')
    for index in range(len(floor_card)):
        print("Card[", index, "] = ", floor_card[index])
    
    print(floor_price_sats, floor_runes, floor_usd)
    
    # Text associated with rune symbol
#    floor_sats_per_runes = floor_card[2]
#    floor_marketcap_btc = sat2btc(floor_price_sats*total_supply)
#    floor_marketcap_usd = floor_unit_price*total_supply
#    floor_card = (floor_price_sats, floor_unit_price, floor_runes, floor_usd, floor_price_btc, marketcap_btc, marketcap_usd, sats_per_runes)

   # TODO: Second lowest card
    #second_card = (second_price_sats, second_unit_price, second_runes, second_usd, second_price_btc, marketcap_btc, marketcap_usd, sats_per_runes)
#    print(f"Floor listing is: {floor_card}")
    
    driver.quit()
#    return floor_card


def market_cap(rune):
    (floor_price_sats, unit_price, floor_runes, floor_usd, price_btc, marketcap_btc, marketcap_usd, sats_per_runes) = fetch(rune)
    
    return (marketcap_btc, marketcap_usd)

ticker='WANKO•MANKO•RUNES'
fetch(ticker)
