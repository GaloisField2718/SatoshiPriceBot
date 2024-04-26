from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC

###########################################################
########            UTILS               ###################
###########################################################

from bs4 import BeautifulSoup
import json
import requests as req

def parse_rune_name(rune):
    dot = '.'
    html_parse = '%E2%80%A2'
    spacer = '•'
    rune = rune.upper()
    if rune.find(dot) != 0:
        rune_name = rune.replace(dot, spacer)
    elif rune.find(html_parse) != 0:
        rune_name = rune.replace(html_parse, spacer)
    return rune_name

def get_supply(rune):
    rune_name = parse_rune_name(rune)
    response = req.get(f'http://94.16.123.98:8080/rune/{rune_name}')
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')
    supply_text = soup.find('dt', string='supply').find_next_sibling('dd').text
    supply_float = float(supply_text.split()[0].replace(',', ''))
    return supply_float

def parse_rune_info(rune_info):
    # Parse the JSON data
    data = rune_info['entry']

    # Construct the formatted message
    formatted_message = (
        f"Spaced Rune: {data['spaced_rune']}\n"
        f"📸 Inscription: https://ordinals.com/content/{rune_info['parent']} \n"
        f"Id: {rune_info['id']} \n"
        f"Mintable: {'✅' if rune_info['mintable'] else '❌'}\n"
        f"\n \t\t ---- GENERAL INFO ---\n\n"
        f"Block: {data['block']}\n"
        f"Symbol: {data['symbol']}\n"
        f"Number: {data['number']}\n"
        f"Timestamp: {data['timestamp']}\n"
        f"Burned: {data['burned']}\n"
        f"Mints: {data['mints']}\n"
        f"Premine: {data['premine']}\n"
        f"Divisibility: {data['divisibility']}\n"
        f"Etching: {data['etching']}\n"
        f"Turbo: {'✅' if data['turbo'] else '❌'}\n"
        "Terms:\n"
        f"  - Amount: {data['terms']['amount']}\n"
        f"  - Cap: {data['terms']['cap']}\n"
        f"  - Height: {data['terms']['height']}\n"
        f"  - Offset: {data['terms']['offset']}"
    )

    return formatted_message


def get_info(rune):
    rune_name = parse_rune_name(rune)
    url = f'http://94.16.123.98:8080/rune/{rune_name}'
    response = req.get(url, headers={"Accept":"application/json"})
    rune_info = json.loads(response.text)
    inscription = rune_info['parent']
    rune_id = rune_info['id']
    mintable = rune_info['mintable']
    rune_info = rune_info['entry']
    return (inscription, rune_id, mintable, rune_info)

def sat2btc(sats):
    return sats/(10**8)

def btc2sat(btc):
    return btc*10**8

def debugCard(card):
    for index in range(len(card)):
        print("Card[", index, "] = ", card[index])


############################################################

def floor_listing(rune):
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    
    rune_name = parse_rune_name(rune)
    driver.get(f'https://unisat.io/runes/market?tick={rune_name}')
    wait = WebDriverWait(driver, 30)
    floor_price_sats = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "price")))
    floor_price_sats = driver.find_element(By.XPATH, '//div[contains(@class, "price-line")]/span[contains(@class, "price")]')
    
    xpath = "//*[@id='rc-tabs-0-panel-1']/div/div[1]/div[1]"
    floor_card_info = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
    floor_card_info = driver.find_element(By.XPATH, xpath)
    
    floor_card = floor_card_info.text.split('\n')
    rune_spaced_name = floor_card[0]
    runes_amount = float(floor_card[1].replace(',',''))
    text_sats_symbol = floor_card[2]
    text_unit_price_usd = floor_card[3]
    incomplete_outpoint = floor_card[4]
    total_amount_btc = float(floor_card[5])
    text_total_amount_usd = floor_card[6]
    
    message = ""
    card = floor_card
    for index in range(len(card)-1):
        message +=f"Card[ {index} ] = {card[index]}\n"
    
    message += f"{text_sats_symbol} ({text_unit_price_usd}).\n"
    (btc_marketcap, usd_marketcap) = get_marketcap(rune)
    message +=f"👉 Marketcap: ${'{:,}'.format(usd_marketcap)} = {btc_marketcap}BTC."
    
    return message

  
def fetch(rune):
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    
    rune_name = parse_rune_name(rune)
    driver.get(f'https://unisat.io/runes/market?tick={rune_name}')
    wait = WebDriverWait(driver, 30)
    floor_price_sats = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "price")))
    floor_price_sats = driver.find_element(By.XPATH, '//div[contains(@class, "price-line")]/span[contains(@class, "price")]')
    
    xpath = "//*[@id='rc-tabs-0-panel-1']/div/div[1]/div[1]"
    floor_card_info = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
    floor_card_info = driver.find_element(By.XPATH, xpath)
    
    floor_card = floor_card_info.text.split('\n')
#    debugCard(floor_card)
   
    text_sats_symbol = floor_card[2]
    text_unit_price_usd = floor_card[3]
    floor_unit_price_usd = float(text_unit_price_usd.replace('$', ''))
    floor_price_sats = floor_price_sats.text.replace(',','')     
    try:
        floor_price_sats = int(floor_price_sats)
    except ValueError:
        floor_price_sats = float(floor_price_sats)
    floor_price_btc = sat2btc(floor_price_sats)
   
    total_supply = get_supply(rune)
    
    btc_marketcap = floor_price_btc*total_supply
    sats_marketcap = floor_price_sats*total_supply
    usd_marketcap = floor_unit_price_usd*total_supply

    driver.quit()
    
    return (text_sats_symbol, floor_unit_price_usd, floor_price_sats, floor_price_btc, usd_marketcap, btc_marketcap)
   
# TODO: Handle second, third, etc.
#    xpath_second = "//*[@id='rc-tabs-1-panel-1']/div/div[1]/div[2]"


def get_marketcap(rune):
    (text_sats_symbol, floor_unit_price_usd, floor_price_sats, floor_price_btc, usd_marketcap, btc_marketcap) = fetch(rune)

    return (btc_marketcap, usd_marketcap)

def get_floor_prices(rune):
    (text_sats_symbol, floor_unit_price_usd, floor_price_sats, floor_price_btc, usd_marketcap, btc_marketcap) = fetch(rune)

    return (floor_unit_price_usd, floor_price_sats, floor_price_btc)


def get_sats_symbol(rune):
    (text_sats_symbol, floor_unit_price_usd, floor_price_sats, floor_price_btc, usd_marketcap, btc_marketcap) = fetch(rune)

    return text_sats_symbol


#runes = ['SATOSHI•NAKAMOTO', 'MEME•ECONOMICS', 'WANKO•MANKO•RUNES', 'BITCOIN•DRUG•MONEY', 'VIVA•LASOGETTE']
#for rune in runes:
#    floor_listing(rune)
