
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC

def fetch(token):
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    driver.get(f'https://unisat.io/market/brc20?tick={token}')
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "price")))
    price_sats = driver.find_element(By.XPATH, '//div[contains(@class, "price-line")]/span[contains(@class, "price")]')
    try :
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "inscription-name  ")))
        amount_oshi = driver.find_element(By.XPATH, '//div[contains(@class, "content display-domain white")]/div[contains(@class, "inscription-name")]')
    except ERROR:
        wait.unit(EC.presence_of_element_located((By.CLASS_NAME, "inscription-name too-long")))
        amount_oshi = driver.find_element(By.XPATH,'//div[contains(@class, "content display-domain white")]/div[contains(@class, "inscription-name too-long")]')
 
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "usd")))
    price_usd = driver.find_element(By.XPATH, '//div[contains(@class, "price-line")]/span[contains(@class, "usd")]')
    xpath = "//*[@id='rc-tabs-0-panel-1']/div/div/div[1]/div[2]/div[3]/span[1]"
    price_btc = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
    price_btc = driver.find_element(By.XPATH, xpath)
    try :
        price_sats = int(price_sats.text)
    except ValueError:
        price_sats = float(price_sats.text)

    amount_oshi = (amount_oshi.text).replace(',','')
    amount_oshi = int(amount_oshi)
    price_usd = price_usd.text
    price_btc = round(float(price_btc.text),8)
    
    driver.quit()

    return (price_sats, amount_oshi, price_usd, price_btc)


