from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import (
    NoSuchWindowException,
    InvalidSessionIdException,
    WebDriverException,
    NoSuchElementException,
    ElementClickInterceptedException,
    StaleElementReferenceException,
    ElementNotInteractableException
)
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json, time, traceback, re, clipboard, random, pyautogui, ctypes,os
from typing import Dict, Any, List, Optional
from datetime import datetime
from urllib.parse import urlparse

from module import Common

def run(driver, text):
    
    try :
        subTitle = text.replace("**", "")
   
        content_wrap = driver.find_element(By.CLASS_NAME, "se-components-wrap")
        text_field = content_wrap.find_elements(By.CLASS_NAME, "se-text")[-1]
        text_field.click()
        time.sleep(0.5)

        actions = ActionChains(driver)
        actions.key_down(Keys.SHIFT).send_keys(Keys.HOME).key_up(Keys.SHIFT).perform()
        time.sleep(1)
        
        toolbar = driver.find_element(By.CLASS_NAME , "se-contents-toolbar-wrap")
        btnquotation = toolbar.find_element(By.CLASS_NAME , "se-toolbar-item-to-quotation").find_element(By.TAG_NAME, "button")
        btnquotation.click()
        time.sleep(0.5)
        
    except Exception as e :
        print(e)
        traceback.print_exc()
   