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

def run(driver):
    
    try :
        actions = ActionChains(driver)

        while True:
            try:
                content_wrap = driver.find_element(By.CLASS_NAME, "se-components-wrap")
                text_fields = content_wrap.find_elements(By.CLASS_NAME, "se-text")
                if not text_fields:
                    raise Exception("No text fields found")
                text_fields[-1].click()
                break
            except Exception as e:
                time.sleep(0.02)
                actions.send_keys(Keys.PAGE_DOWN).perform()
                
        actions.key_down(Keys.CONTROL).send_keys("a").key_up(Keys.CONTROL).perform()

        time.sleep(0.05)

        btn_align_list = driver.find_element(By.CLASS_NAME, "se-toolbar-item-align")
        btn_align_list.click()

        time.sleep(0.05)

        align_option = "center"
        
        # 정렬 옵션 클릭
        if align_option == "left":
            btn_align_list.find_element(By.CLASS_NAME, "se-toolbar-option-align-left-button").click()
        elif align_option == "center":
            btn_align_list.find_element(By.CLASS_NAME, "se-toolbar-option-align-center-button").click()
        elif align_option == "right":
            btn_align_list.find_element(By.CLASS_NAME, "se-toolbar-option-align-right-button").click()
        elif align_option == "original":
            btn_align_list.find_element(By.CLASS_NAME, "se-toolbar-option-align-justify-button").click()
        else:
            raise ValueError("align_option must be one of: left, center, right, original")

        btnFont = driver.find_element(By.CLASS_NAME, "se-toolbar-item-font-family")
        btnFont.click()
        time.sleep(1)
        
        while True :
            if len(driver.find_elements(By.CLASS_NAME , "se-toolbar-option-font-family")) > 0 :
                break
            
            time.sleep(0.1)

        btnFontList = driver.find_element(By.CLASS_NAME, "se-toolbar-option-font-family").find_elements(By.TAG_NAME, "button")
        btnFontList[1].click()
        
    except Exception as e :
        print(e)
        traceback.print_exc()
   