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

import io
from PIL import Image
import win32clipboard

def run(driver, image_path):
    
    try :
        time.sleep(0.2)
        
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
        time.sleep(0.5)
        
       
        active = driver.switch_to.active_element
        # active.send_keys(Keys.CONTROL, "v")
        
        actions = ActionChains(driver)
        actions.key_down(Keys.CONTROL).send_keys("v").key_up(Keys.CONTROL).perform()

        time.sleep(3)
        
        while True :
            if len(driver.find_elements(By.CLASS_NAME , "se-popup-progress")) > 0 :
                time.sleep(0.5)
                
            if len(driver.find_elements(By.CLASS_NAME , "se-popup-container")) > 0 :
                if len(driver.find_element(By.CLASS_NAME , "se-popup-container").find_elements(By.CLASS_NAME , "se-popup-button-confirm")) > 0 :
                    driver.find_element(By.CLASS_NAME , "se-popup-container").find_element(By.CLASS_NAME , "se-popup-button-confirm").click()
                
                    active.send_keys(Keys.CONTROL, "v")
                    
            if len(driver.find_elements(By.CLASS_NAME , "se-is-progress")) == 0 :
                break
                

        content_wrap = driver.find_element(By.CLASS_NAME, "se-components-wrap")
        content_wrap.find_elements(By.CLASS_NAME, "se-section-image")[-1].click()
        time.sleep(0.5)


        imgtoolbar = driver.find_elements(By.CLASS_NAME , "se-context-toolbar-image")[0]
        imgtoolbar.find_element(By.CLASS_NAME, "se-toolbar-item-object-arrangement").find_elements(By.TAG_NAME, "button")[1].click()
           
        
    except Exception as e :
        print(e)
        traceback.print_exc()

def make_group_image(driver, image_count: int, current_subject: int, timeout: int = 20):
    
    wait = WebDriverWait(driver, timeout)

    is_make_group_image = random.randrange(2)          # 0 or 1
    max_selected_image = random.randrange(2) + 2       # 2 or 3

    if is_make_group_image != 1:
        return

    content_wrap = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "se-components-wrap")))
    image_fields = content_wrap.find_elements(By.CLASS_NAME, "se-image")
    time.sleep(1)

    if not image_fields or len(image_fields) < 2:
        return

    start_index = len(image_fields) - image_count
    end_index = len(image_fields) - 1

    # 방어: start_index가 음수가 되는 경우 보정
    if start_index < 0:
        start_index = 0

    if image_count < 3:
        # 마지막 2장 합치기
        drag_and_drop_image(driver, image_fields, image_fields, len(image_fields) - 2, len(image_fields) - 1)
    else:
        # 최근 이미지 구간에서 2개 랜덤 선택
        random_indexes = get_random_numbers_in_range(start_index, end_index, 2)
        drag_and_drop_image(driver, image_fields, image_fields, random_indexes[0], random_indexes[1])

        if max_selected_image == 3:
            # DOM 갱신
            image_fields = content_wrap.find_elements(By.CLASS_NAME, "se-image")
            time.sleep(1)

            start_index = len(image_fields) - (image_count - 2)
            end_index = len(image_fields) - 1
            if start_index < 0:
                start_index = 0

            random_indexes = get_random_numbers_in_range(start_index, end_index, 1)

            image_group_fields = content_wrap.find_elements(By.CLASS_NAME, "se-imageStrip2")
            if not image_group_fields:
                return

            drag_and_drop_image(
                driver,
                image_fields,
                image_group_fields,
                random_indexes[0],
                len(image_group_fields) - 1
            )


def get_random_numbers_in_range(start_index: int, end_index: int, max_count: int) -> List[int]:
    if end_index < start_index:
        start_index, end_index = end_index, start_index

    population = list(range(start_index, end_index + 1))
    if not population:
        return []

    max_count = min(max_count, len(population))
    return random.sample(population, max_count)


def drag_and_drop_image(driver, from_elements, to_elements, from_index: int, to_index: int):
    from_img = from_elements[from_index].find_element(By.TAG_NAME, "img")
    to_img = to_elements[to_index].find_element(By.TAG_NAME, "img")

    actions = ActionChains(driver)
    time.sleep(0.5)

    from_img.click()
    time.sleep(0.5)

    actions.click_and_hold(from_img).move_to_element(to_img).release(to_img).perform()


def set_photo_mosaic(driver, current_photo, timeout: int = 20):
    wait = WebDriverWait(driver, timeout)

    content_wrap = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "se-components-wrap")))

    image_fields = content_wrap.find_elements(By.CLASS_NAME, "se-image")
    if not image_fields:
        return

    image_fields[-1].click()
    time.sleep(0.5)

    # 컨텍스트 툴바(이미지)에서 편집 클릭
    image_tools = content_wrap.find_elements(By.CLASS_NAME, "se-context-toolbar-image")
    if not image_tools:
        return

    btn_image_edit_wrap = image_tools[0].find_element(By.CLASS_NAME, "se-toolbar-item-image-edit")
    btn_image_edit_wrap.click()

    # 모자이크 버튼 로딩 대기: npe_control_area 내 npe_mosaic
    def mosaic_ready(d):
        areas = d.find_elements(By.CLASS_NAME, "npe_control_area")
        if not areas:
            return False
        return len(areas[0].find_elements(By.CLASS_NAME, "npe_mosaic")) > 0

    wait.until(mosaic_ready)

    btn_edit_mosaic = driver.find_elements(By.CLASS_NAME, "npe_control_area")[0].find_element(By.CLASS_NAME, "npe_mosaic")
    time.sleep(1)
    btn_edit_mosaic.click()
    time.sleep(0.1)

    # 자동 얼굴 텍스트 노출 대기: _txt_auto_face-text
    wait.until(lambda d: len(d.find_elements(By.CLASS_NAME, "_txt_auto_face-text")) > 0)

    # 자동 얼굴 모자이크 토글 클릭
    btn_auto_face_mosaic = driver.find_element(By.CLASS_NAME, "npe_control_mosaic").find_element(By.CLASS_NAME, "npe_toggle_button")
    btn_auto_face_mosaic.click()
    time.sleep(1)

    # 완료(적용) 버튼 클릭
    btn_finish = driver.find_elements(By.CLASS_NAME, "npe_btn_area")[0].find_element(By.CLASS_NAME, "npe_btn_submit")
    btn_finish.click()
    time.sleep(1)

    # 에디터 복귀 대기: se-canvas-bottom 나타날 때까지
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "se-canvas-bottom")))
