import os

from main import DEBUG

from selenium import webdriver  
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC 



def driver_get_html(url, tags):
    chrome_options = Options()
    #chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(executable_path="./driver/chromedriver", options=chrome_options)
    driver.get(url)  
    for tag in tags:
        if(DEBUG): print(f'[DRIVER TRYING SEARCH]: {tag[2]}')
        try:
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, tag[2]))
            )
        except:
            if(DEBUG): print(f'[DRIVER FAILED SEARCH]: {tag[2]}')
            pass
        finally:
            if(DEBUG): print(f'[DRIVER DONE SEARCH]: {tag[2]}')
            pass


    html = driver.page_source
    driver.close() 
    return html
