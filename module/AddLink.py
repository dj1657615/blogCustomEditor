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

def run(driver, link):
    
    try :
        while True :
            if len(driver.find_elements(By.CLASS_NAME , "se-components-wrap")) > 0 :
                break
            
            time.sleep(0.1)

        contentWrap = driver.find_element(By.CLASS_NAME , "se-components-wrap")
        imageFields = contentWrap.find_elements(By.CLASS_NAME , "se-module-image")
        time.sleep(0.2)
       
        imageFields[-1].click()
        time.sleep(0.2)

        btnLink = driver.find_element(By.CLASS_NAME , "se-toolbar-item-link").find_element(By.TAG_NAME , "button")
        btnLink.click()
        time.sleep(0.5)
        
        start_time = time.time()
        while True :
            if len(driver.find_elements(By.CLASS_NAME , "se-custom-layer-link-input")) > 0 :
                break
            if time.time() - start_time > 20:
                break
            
            time.sleep(0.1)
           
        linkIpuntField = driver.find_element(By.CLASS_NAME , "se-custom-layer-link-input")
        linkIpuntField.click()
        time.sleep(0.2) 
            
        actions = ActionChains(driver)
        actions.key_down(Keys.LEFT_CONTROL).send_keys("a").key_up(Keys.LEFT_CONTROL).perform()
        time.sleep(0.1)
        actions.key_down(Keys.BACK_SPACE).perform()
        time.sleep(0.1)
        
        clipboard.copy(link)
        time.sleep(0.5)
        
        actions.key_down(Keys.LEFT_CONTROL).send_keys("v").key_up(Keys.LEFT_CONTROL).perform()
        time.sleep(0.5)
        
        btnAddLink = driver.find_element(By.CLASS_NAME , "se-custom-layer-link-apply-button")
        btnAddLink.click()
        
    except Exception as e :
        print(e)
        traceback.print_exc()
   