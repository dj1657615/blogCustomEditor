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

def run(driver, change_text_element, mapName):
    
    try :
        change_text_element.click()
        time.sleep(1)

        # 툴바 스티커 버튼: li[3]
        start_time = time.time()
        while True :
            if len(driver.find_elements(By.CLASS_NAME,"se-document-toolbar")) > 0 :
                break
            if time.time() - start_time > 20:
                return True
            time.sleep(0.1)
        
        btnMapToolbar = driver.find_element(By.CLASS_NAME,"se-document-toolbar").find_elements(By.TAG_NAME,"li")
        btnMapToolbar[3].click()
        time.sleep(0.3)
        
        # 우측 스티커바
        start_time = time.time()
        while True :
            if len(driver.find_elements(By.CLASS_NAME,"se-panel-tab-list")) > 0 :
                break
            if time.time() - start_time > 20:
                return True
            time.sleep(0.1)
        
        btnStickerList = driver.find_element(By.CLASS_NAME,"se-panel-tab-list").find_elements(By.TAG_NAME,"li")
        time.sleep(0.3)
        
        randomIndex = random.randint(1, 5)
        time.sleep(0.1)
        btnStickerList[randomIndex].click()
        time.sleep(0.3)
        
        # 스티커 목록
        start_time = time.time()
        while True :
            if len(driver.find_elements(By.CLASS_NAME,"se-sidebar-item")) > 0 :
                break
            if time.time() - start_time > 20:
                return True
            time.sleep(0.1)
            
        current_stickers = driver.find_elements(By.CLASS_NAME, "se-sidebar-item")
        random_select = random.randrange(len(current_stickers))
        time.sleep(0.2)
        
        current_stickers[random_select].click()
        time.sleep(0.2)
        
        close_btn = driver.find_element(By.CLASS_NAME, "se-sidebar-close-button")
        close_btn.click()
        time.sleep(0.5)

    except Exception as e :
        print(e)
        traceback.print_exc()