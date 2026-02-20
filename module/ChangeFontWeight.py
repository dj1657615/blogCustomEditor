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

def run(driver, content_element):
    
    try :
        print(f"볼드체를 적용합니다")
        p_tags = content_element.find_elements(By.TAG_NAME, "p")
        pattern = re.compile(r"@@(.*?)@@")

        for p in p_tags:
            text = p.text or ""
            matches = list(pattern.finditer(text))
            if not matches:
                continue

            for m in reversed(matches):
                word = m.group(1)
                start = m.start(1)
                end = m.end(1)
                position_from_end = len(text) - end + 2  

                # 디버그 출력(원하면 주석 처리)
                print(f"단어: {word}")
                print(f"시작 위치 (앞에서): {start}")
                print(f"끝 위치 (뒤에서): {position_from_end}")

                try:
                    p.find_element(By.TAG_NAME, "span")
                except Exception:
                    pass
                time.sleep(0.2)

                # p 클릭해서 포커스
                p.click()
                time.sleep(0.2)

                # END 키: 줄/문장 끝으로 이동 (환경에 따라 HOME/END 동작이 다를 수 있음)
                p.send_keys(Keys.END)
                time.sleep(0.2)

                # 뒤에서 position_from_end-2 만큼 LEFT 이동
                for _ in range(max(position_from_end - 2, 0)):
                    p.send_keys(Keys.ARROW_LEFT)
                time.sleep(0.5)

                # @@ 2글자 삭제 (Delete 2회)
                p.send_keys(Keys.DELETE)
                p.send_keys(Keys.DELETE)
                time.sleep(0.5)

                # 단어 길이만큼 Shift+Left로 선택
                for _ in range(len(word)):
                    p.send_keys(Keys.SHIFT, Keys.ARROW_LEFT)
                time.sleep(0.5)

                # Bold 버튼 클릭 (Java: se-toolbar-item-bold 2번째 요소의 button)
                # 페이지 구조에 따라 인덱스가 깨질 수 있으니 필요하면 selector 개선 권장
                btn_bold = driver.find_elements(By.CLASS_NAME, "se-toolbar-item-bold")[1].find_element(By.TAG_NAME, "button")
                btn_bold.click()
                time.sleep(0.2)

                # 커서 한 칸 왼쪽 이동
                p.send_keys(Keys.ARROW_LEFT)

                # 남은 @@ 2글자 제거 (Backspace 2회)
                p.send_keys(Keys.BACKSPACE)
                p.send_keys(Keys.BACKSPACE)
                time.sleep(0.05)

                # 이 시점에서 텍스트가 변경됐으니 다음 매치 처리 전에 최신 텍스트로 갱신
                text = p.text or ""
    
    except Exception as e :
        print(e)
        traceback.print_exc()
   