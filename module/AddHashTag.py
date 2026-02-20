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

def run(driver, hashTags):
    
    try :  
        start_time = time.time()
        while True :
            if len(driver.find_elements(By.CLASS_NAME,"se-document-toolbar")) > 0 :
                break
            if time.time() - start_time > 20:
                return True
            time.sleep(0.1)
       
    except Exception as e :
        print(e)
        traceback.print_exc()
   