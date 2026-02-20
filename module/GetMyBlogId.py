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

def run(driver, url):
    
    try :
        print(f"블로그 에디터를 엽니다")
        
        driver.get(url)
    
        start_time = time.time()
        while True :
            if len(driver.find_elements(By.CLASS_NAME,"menu_my_blog")) > 0 :
                break
            if time.time() - start_time > 20:
                return True
            time.sleep(0.1)
            
        btnMyBlog = driver.find_element(By.CLASS_NAME,"menu_my_blog").find_elements(By.TAG_NAME, "a")
        btnMyBlog[1].click()
        print(f"내 블로그 버튼을 클릭합니다")
        
        
        handles = driver.window_handles
        while True :
            if len(handles) >= 2 :
                break
            time.sleep(0.1)
        
        driver.switch_to.window(driver.window_handles[1])
        time.sleep(1)

        iframe = driver.find_element(By.ID, "mainFrame")
        driver.switch_to.frame(iframe)
        time.sleep(1)
        
        popups = driver.find_elements(By.CLASS_NAME, "se-popup-container")
        if popups:
            try:
                cancel_btn = popups[0].find_element(By.CLASS_NAME, "se-popup-button-cancel")
                cancel_btn.click()
                time.sleep(0.5)
            except Exception:
                pass
        time.sleep(0.5)
            
        helps = driver.find_elements(By.CLASS_NAME, "se-help-container")
        if helps:
            try:
                close_btn = helps[0].find_element(By.CLASS_NAME, "se-help-panel-close-button")
                close_btn.click()
                time.sleep(0.5)
            except Exception:
                pass
        time.sleep(0.5)
            
        current_url = driver.current_url

        parsed = urlparse(current_url)
        path = parsed.path.rstrip("/")
        blog_id = path.split("/")[-1] if path else ""

        return blog_id
    
    except Exception as e :
        print(e)
        traceback.print_exc()
   