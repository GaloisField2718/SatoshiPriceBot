from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC

def fetch(token):
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    driver.get(f'https://atomicalmarket.com/market/token/{token}')
    wait = WebDriverWait(driver, 10)
    price_sats = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "marketpages_MainText__6kpIu")))
    price_sats = driver.find_element(By.XPATH, '/html/body/main/div[5]/div/div/div[1]/div/div[1]/div/div/span')
    amount_atom = driver.find_element(By.XPATH, '/html/body/main/div[5]/div/div/div[1]/div/div[1]/div/div/h3')
    price_usd = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "marketpages_MarketUSDValue__IJv2U")))
    price_usd = driver.find_element(By.XPATH, '/html/body/main/div[5]/div/div/div[1]/div/div[1]/div/div/p')
    xpath = "/html/body/main/div[5]/div/div/div[1]/div/div[2]/div"
    price_btc = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
    price_btc = driver.find_element(By.XPATH, xpath)
    price_btc.replace(',', '.')
    
    price_sats = int(price_sats.text)
    amount_atom = (amount_oshi.text).replace(',','')
    amount_atom = int(amount_oshi)
    price_usd = price_usd.text
    price_btc = round(float(price_btc.text),8)
    
    driver.quit()

    return (price_sats, amount_oshi, price_usd, price_btc)


fetch('atom')
