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

from module import AddImage
from module import Common

import io
from PIL import Image
import win32clipboard

def run(driver, image_path):
    
    try :
        handles = driver.window_handles
        while True :
            if len(handles) >= 2 :
                break
            time.sleep(0.1)
        driver.switch_to.window(driver.window_handles[2])
        time.sleep(2)
        
        
        iframe = driver.find_element(By.ID, "mainFrame")
        driver.switch_to.frame(iframe)
        time.sleep(2)
        
        Common.focus_editor_end(driver)
        
        image = Image.open(image_path)

        with io.BytesIO() as output:
            bmp = image.convert("RGB")
            bmp.save(output, "BMP")
            data = output.getvalue()[14:]

        win32clipboard.OpenClipboard()
        try:
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
        finally:
            win32clipboard.CloseClipboard()
        
       
        active = driver.switch_to.active_element
        # active.send_keys(Keys.CONTROL, "v")
        
        actions = ActionChains(driver)
        actions.key_down(Keys.CONTROL).send_keys("v").key_up(Keys.CONTROL).perform()

        time.sleep(3)
        
        while True :
            if len(driver.find_elements(By.CLASS_NAME , "se-popup-progress")) > 0 :
                time.sleep(0.5)
                
            if len(driver.find_elements(By.CLASS_NAME , "se-popup-container")) > 0 :
                if len(driver.find_elements(By.CLASS_NAME , "se-popup-container").find_elements(By.TAG_NAME , "button")) > 0 :
                    driver.find_element(By.CLASS_NAME , "se-popup-container").find_element(By.TAG_NAME , "button").clikc()
                
                    active.send_keys(Keys.CONTROL, "v")
                    
            if len(driver.find_elements(By.CLASS_NAME , "se-is-progress")) == 0 :
                break

                    
        contentWrap = driver.find_element(By.CLASS_NAME , "se-components-wrap")
        imageFields = contentWrap.find_elements(By.CLASS_NAME , "se-module-image")
        time.sleep(0.2)
        
        imageFields[-1].click()
        time.sleep(0.2)
        actions.key_down(Keys.CONTROL).send_keys("c").key_up(Keys.CONTROL).perform()
        time.sleep(0.2)
        
        handles = driver.window_handles
        while True :
            if len(handles) >= 2 :
                break
            time.sleep(0.1)
        driver.switch_to.window(driver.window_handles[1])
        time.sleep(2)
        
        iframe = driver.find_element(By.ID, "mainFrame")
        driver.switch_to.frame(iframe)
        time.sleep(2)
                    
        actions.key_down(Keys.CONTROL).send_keys("v").key_up(Keys.CONTROL).perform()
        time.sleep(0.2)
        
    except Exception as e :
        print(e)
        traceback.print_exc()