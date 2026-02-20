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

def run(driver, blogId):
    
    try :
        print(f"블로그 에디터를 엽니다")
        url = f"https://blog.naver.com/{blogId}?Redirect=Write&"
        
        driver.get(url)
        time.sleep(1)
    
        count = 0
        start_time = time.time()
        while True :           
            print(url)
            print(driver.current_url)
            if url in driver.current_url : 
                break
            
            if count > 100 :
                count = 0
                driver.get(url)
                
            time.sleep(0.1)
            count += 1 
        
        time.sleep(1)
        
        print(f"팝업을 체크합니다")
        closePopup(driver)
    
    except Exception as e :
        print(e)
        traceback.print_exc()
   
   
def closePopup(driver) :
    
    count = 0
    closeCount = 0
    while True :
        try:
            iframe = driver.find_element(By.ID, "mainFrame")
            driver.switch_to.frame(iframe)
            time.sleep(2)
            
            if len(driver.find_elements(By.CLASS_NAME, "se-popup-container")) > 0 :
                btnNoContinuePost = driver.find_element(By.CLASS_NAME, "se-popup-container").find_element(By.CLASS_NAME, "se-popup-button-cancel")
                time.sleep(0.2)
                
                btnNoContinuePost.click()
                time.sleep(0.5)
                closeCount += 1
            
            if len(driver.find_elements(By.CLASS_NAME, "se-help-container")) > 0 :
                btnNoContinuePost = driver.find_element(By.CLASS_NAME, "se-help-container").find_element(By.CLASS_NAME, "se-help-panel-close-button")
                time.sleep(0.2)
                
                btnNoContinuePost.click()
                time.sleep(0.5)
                closeCount += 1
            
            driver.switch_to.parent_frame()
            
            if closeCount >= 2 :
                break
            
            if count >= 7:
                break
            
            count +=1 
            time.sleep(0.1)
            
            print(count)
            
        except Exception as e :
            print(f"close pop up error! : {e}") 