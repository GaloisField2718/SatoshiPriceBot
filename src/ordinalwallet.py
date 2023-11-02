
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC
#from urllib3.util import ssl_ as ssl
# then use ssl.DEFAULT_CIPHERS
from cfscrape import create_scraper
import time

def fetch():
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    scraper = create_scraper()
    # Scrape the url first to trigger Cloudflare challenge
    scraper.get("https://ordinalswallet.com/brc20/OSHI")
    time.sleep(5) # Pauses script for 5 seconds
    # Now the cookies are captured in scraper  
    cookies = scraper.cookies

    # Add cookies to Selenium driver
    for cookie in cookies:
        driver.add_cookie(cookie)
    time.sleep(5) # Pauses script for 5 seconds
    wait = WebDriverWait(driver, 10) 
    driver.get("https://ordinalswallet.com/brc20/OSHI")
    time.sleep(5) # Pauses script for 5 seconds

    html = driver.page_source
    
    print(html)

    driver.quit()
    
    return html

fetch()
