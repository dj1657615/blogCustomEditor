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
        title = sanitize_text(text)

        content_wrap = driver.find_element(By.CLASS_NAME, "se-components-wrap")
        title_field = content_wrap.find_elements(By.CLASS_NAME, "se-section")[0]
        title_field.click()
        time.sleep(1)

        active = driver.switch_to.active_element
        # 기존 내용 완전 삭제 
        active.send_keys(Keys.CONTROL, 'a')
        active.send_keys(Keys.DELETE)
        time.sleep(0.1)
            
        Common.copyAndInput(title, active)
       
    except Exception as e :
        print(e)
        traceback.print_exc()
   
def sanitize_text(s: str) -> str:
    if s is None:
        return ""
    # 숨은 공백/제어문자 제거
    s = (s
        .replace('\u00A0', ' ')  # NBSP
        .replace('\u2009', ' ')  # thin space
        .replace('\u202F', ' ')  # narrow NBSP
        .replace('\u200B', '')   # ZWSP
        .replace('\uFEFF', '')   # BOM
    )
    # 연속 공백 1개로
    s = re.sub(r'\s+', ' ', s).replace("**", "")
    return s.strip()
