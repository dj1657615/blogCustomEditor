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

from module import Common

def run(driver, tags):
    
    try :
        start_time = time.time()
        while True :
            if len(driver.find_elements(By.CLASS_NAME,"publish_btn__m9KHH")) > 0 :
                break
            if time.time() - start_time > 20:
                return True
            time.sleep(0.1)
        print("게시 버튼 찾기 완료!!")

        btnAddNewPost = driver.find_element(By.CLASS_NAME, "publish_btn__m9KHH")
        btnAddNewPost.click()
        time.sleep(1)
        print("게시 버튼 클릭 완료!!")
        
        
        if tags:
            tagInput = driver.find_element(By.CLASS_NAME, "tag_textarea__CD7pC")
            tagInput.click()
            time.sleep(0.5)

            actions = ActionChains(driver)
            for hashtag in tags:
                while True:
                    try:
                        hashtag = hashtag.replace("#", "")
                        clipboard.copy(hashtag)
                        time.sleep(0.3)

                        actions.key_down(Keys.CONTROL).send_keys("v").key_up(Keys.CONTROL).perform()
                        time.sleep(0.3)

                        actions.send_keys(Keys.SPACE).perform()
                        time.sleep(0.3)
                        break

                    except Exception as e:
                        pass
            
        start_time = time.time()
        while True :
            if len(driver.find_elements(By.CLASS_NAME,"confirm_btn__WEaBq")) > 0 :
                break
            if time.time() - start_time > 20:
                return True
            time.sleep(0.1)
        print("발행 버튼 찾기 완료!!")

        btnAddNewPostConfirm = driver.find_element(By.CLASS_NAME, "confirm_btn__WEaBq")
        btnAddNewPostConfirm.click()
        time.sleep(1)
        print("발행 버튼 클릭 완료!!")
    
    except Exception as e :
        print(e)
        traceback.print_exc()