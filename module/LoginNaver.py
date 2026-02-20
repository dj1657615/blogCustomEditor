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

def run(driver, url, id, pw):
    
    try :
        print(f"로그인을 시작합니다")
        print(f"id : {id}")
        print(f"pw : {pw}")
        
        driver.get(url)
    
        start_time = time.time()
        while True :
            if len(driver.find_elements(By.ID,"id")) > 0 :
                break
            if len(driver.find_elements(By.ID,"pw")) > 0 :
                break
            if time.time() - start_time > 20:
                return True
            time.sleep(0.1)
    
        clipboard.copy(id)
        time.sleep(0.5)
        id_field = driver.find_element(By.ID,"id")
        id_field.send_keys(Keys.CONTROL + "v")
        time.sleep(0.5)
        print("아이디 입력 완료!!")
        
        clipboard.copy(pw)
        time.sleep(0.5)
        pw_field = driver.find_element(By.ID,"pw")
        pw_field.send_keys(Keys.CONTROL + "v")
        time.sleep(0.5)
        print("비밀번호 입력 완료!!")
    
        if driver.find_element(By.ID , "smart_LEVEL").get_attribute("value") != "-1" :
            btnIpProtect = driver.find_element(By.CLASS_NAME , "switch_on")
            time.sleep(0.5)
            btnIpProtect.click()
            time.sleep(0.5)
        
        driver.find_elements(By.CLASS_NAME,"btn_login_wrap")[0].find_element(By.CLASS_NAME , "btn_login").click()
    
        if len(driver.find_elements(By.ID , "new.save")) > 0  :
            btnAddNewBrowser = driver.find_element(By.ID , "new.save")
            btnAddNewBrowser.click()

        count = 0
        start_time = time.time()
        while True :
            currentUrl = driver.current_url
            
            if "https://www.naver.com/" in currentUrl :
                return 0
            
            if "https://nid.naver.com/user2/help/idRelease" in currentUrl :
                return 2
            
            if "https://nid.naver.com/user2/help/idSafetyRelease" in currentUrl :
                return 4
            
            if time.time() - start_time > 300:
                return 3
            time.sleep(0.5)
        
    except Exception as e :
        print(e)
        traceback.print_exc()
        return 3
   