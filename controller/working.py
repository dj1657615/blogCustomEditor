# -*- coding: utf-8 -*-

from PyQt5 import  QtCore
from PyQt5.QtCore import *

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
from subprocess import CREATE_NO_WINDOW

from datetime import datetime
from pathlib import Path
import subprocess
import requests

import json, time, traceback, re, clipboard, random, pyautogui, ctypes,os
from typing import Dict, Any, List, Optional, Union
from urllib.parse import urlsplit, parse_qsl, urlencode, urlunsplit

from controller import editImage
from gemini import gemini

from module import (
    MoveWritePage,
    GetMyBlogId,
    LoginNaver,
    Common,
    
    AddGraph,
    AddHashTag,
    AddHiddenimage,
    AddPost,
    AddImage,
    AddIndexTitle,
    AddLine,
    AddLink,
    AddSticker,
    AddText,
    AddTitle,
    AlignAll,
)
from caller import googleSheet

class Thread(QtCore.QThread) :
    
    LOGIN_URL = "https://nid.naver.com/nidlogin.login"
    BLOG_URL = "https://section.blog.naver.com/"
    
    naver_id = ""
    naver_pw = ""
    
    blog_id = ""
    
    current_post_title = ""
    current_post_url = ""
    
    base_ip = ""
    
    picked_keywords = None
    _last_regions_data = None
    _last_jobs_data = None
    
    def run(self):
        self.loop()
          
    def load_campaigns(self, path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
        
    def setNowTime(self) :
        now = datetime.now()
        today_second = now.strftime("%H:%M:%S")
        return today_second   
            
    def waitDelayTime(self,delay_time) :
        min_time = max(delay_time - 0.9, 0.1)  
        max_time = delay_time + 0.9      
        randomTime = round(random.uniform(min_time, max_time), 2)
        
        print(f"{min_time}~{max_time} : {randomTime}초.....")
        
        count = 0
        while count < randomTime:
            time.sleep(0.1)
            count += 0.1
                
    def loop(self) :
        
        print("\n" + f"[{self.setNowTime()}]" + "~~" * 100)
        print(f"[{self.setNowTime()}] loop start!!")
        self.makeDriver()

        while True :
            
            print("\n" + f"[{self.setNowTime()}]" + "~~" * 80)
            
            campaigns = self.load_campaigns("campaign.json")
            print(campaigns[0])
            
            if not campaigns:
                print(f"[{self.setNowTime()}] ❌ 사용 가능한 캠페인이 없습니다.")
                return

            
            while True :
                acc = googleSheet.get_account_min_count_with_cooldown(
                    cooldown_hours=3
                )
                print(f"Google Sheet Account Data : {acc}")
                
                if not acc:
                    print(f"[{self.setNowTime()}] ❌ 사용 가능한 계정이 없습니다.")
                    return
                
                self.naver_id = acc["id"]
                self.naver_pw = acc["pw"]
                row = acc["row"]
            
                #vpn켜기
                # self.connect()
                
                self.ensure_baseline_ip()

                new_ip = self.connect(country="kr")
                print(f"[VPN] connected ip = {new_ip}")
            

                loginResult = self.login(row)
                
                if loginResult :
                    time.sleep(2)
                    break
                else:
                    self.disconnect(timeout=300)   
                    continue
                
        
            self.blog_id = GetMyBlogId.run(driver, self.BLOG_URL)
            
            print(f"[{self.setNowTime()}] first write tab open start !!!")
            MoveWritePage.run(driver, self.blog_id)
            
            print(f"[{self.setNowTime()}] new tab open!!!")
            driver.execute_script("window.open('', '_blank');")
            time.sleep(1)
            new_handles = driver.window_handles[-1] 
            driver.switch_to.window(new_handles)
            
            print(f"[{self.setNowTime()}] second write tab open start !!!")
            MoveWritePage.run(driver, self.blog_id)
            original_handle = driver.window_handles[1]  
            driver.switch_to.window(original_handle)

            postingResultStatus = self.doPosting(campaigns[0])
            print("[DEBUG] postingResultStatus =", postingResultStatus)

            if postingResultStatus == True :
                # (1) account: count+1, used_date 업데이트
                googleSheet.mark_account_used(acc["row"])

                # (2) post: 발행 로그 추가
                published_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                googleSheet.append_post_log(
                    published_date,
                    self.current_post_title or "제목없음",
                    self.current_post_url or driver.current_url,
                    acc["id"]
                )
                
                # 로컬 count 업데이트 (+ 저장)
                if self.picked_keywords and self._last_regions_data and self._last_jobs_data:
                    Common.increment_used_counts(self._last_regions_data, self._last_jobs_data, self.picked_keywords)

                    Common.save_json("regions.json", self._last_regions_data)
                    Common.save_json("jobs.json", self._last_jobs_data)

                    print(f"[{self.setNowTime()}]  count +1 및 저장 완료: {self.picked_keywords}")
            
            #vpn끄기       
            # self.logout()
            self.disconnect(timeout=60)
            
            time.sleep(30)
            print(f"[{self.setNowTime()}] 300초간 대기후 다시 시작")
            self.resetDriver()
            time.sleep(270)
                        
        
    def makeDriver(self) :
        ctypes.windll.kernel32.SetThreadExecutionState(0x80000002)
        
        global driver

        options = webdriver.ChromeOptions()
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--remote-allow-origins=*")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument(f"--window-size=1280,1024")
        options.add_argument("--disable-gpu")
        # options.add_argument(
        #         "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
        # options.set_capability("goog:loggingPrefs", {"performance":"ALL"})

        chrome_path =  "./chromedriver_t.exe"
        service = Service(executable_path=chrome_path)
        service.creation_flags = CREATE_NO_WINDOW
        
        try :
            driver = webdriver.Chrome(service=service, options=options)
            driver.set_window_position(0,0)
        except Exception as e:
            print(f"makeDriver Error : {e}")
            traceback.print_exc()
    
    
    def login(self, row) :
        
        loginStatus = LoginNaver.run(driver, self.LOGIN_URL, self.naver_id, self.naver_pw)
        
        if loginStatus == 2 :
            googleSheet.update_account_status(row, "lock")
            return False
        elif loginStatus == 3 :
            googleSheet.update_account_status(row, "fail")
            return False
        elif loginStatus == 4 :
            googleSheet.update_account_status(row, "protect")
            return False
        
        return True
    
    # def logout(self) :
        
    #     driver.get(self.home_url)
    #     driver.implicitly_wait(10)
    #     try:
    #        while True :
    #         if len(driver.find_elements(By.CLASS_NAME , "MyView-module__btn_logout___bsTOJ"))  > 0:
    #             break
    #         time.sleep(0.05)
        
    #         btnLogout = driver.find_element(By.CLASS_NAME , "MyView-module__btn_logout___bsTOJ")
    #         btnLogout.click()
    #     except Exception as e:
    #         print(e)
    #         pass
    
    def checkError(self) :
        start_time = time.time()
        while True :
            if len(driver.find_elements(By.CLASS_NAME , "error_layerpopup__XOt1j")) > 0 :
                driver.find_element(By.CLASS_NAME,  "ok_btn__mVM4b").click()
                time.sleep(1)
                return True 
            if time.time() - start_time > 5:
                return False  
            time.sleep(0.1)
        
    
    def doPosting(self, data) :
        print(f"[{self.setNowTime()}] posting start")
        
        try:
            region_name, job_name, regions_data, jobs_data = Common.pick_region_job(top_k=50)
        except Exception as e:
            print(f"지역/작업 선택 실패: {e}")
            return
        
        pools = Common.build_pools_min_count(jobs_data)
        print("[POOLS(min-count)]", pools)

        rr = gemini.get_title(region=region_name, main_keyword=job_name, pools=pools)
        print("[Gemini title_generate result]", rr)
    

        title = (rr.get("title") or f"{region_name} {job_name}").strip()
        extra_kw = ""
        if len(title) < 30:
            extra_kw = self.pick_random_extra_keyword(jobs_data)
            if extra_kw:
                # 제목에 자연스럽게 붙이기 (가장 단순한 방식: 끝에 한 칸 + 키워드)
                title = f"{title} {extra_kw}".strip()

        self.current_post_title = title
        print(f"[{self.setNowTime()}] 최종 제목: {title} (len={len(title)})")

        self.picked_keywords = {
            "region": region_name,
            "main": job_name,
            "subKeyword": (rr.get("subKeyword") or "").strip(),
            "target": (rr.get("target") or "").strip(),
            "workSite": (rr.get("workSite") or "").strip(),
            "expandKeyword": (rr.get("expandKeyword") or "").strip(),
            "extraKeyword": extra_kw,
        }


        self._last_regions_data = regions_data
        self._last_jobs_data = jobs_data

        posting_ok = self.render_campaign(region_name, job_name, data)


        # count +1
        # Common.increment_count_by_name(regions_data["regions"], region_name, inc=1)
        # Common.increment_count_by_name(jobs_data["jobs"], job_name, inc=1)

        # # 저장
        # Common.save_json("regions.json", regions_data)
        # Common.save_json("jobs.json", jobs_data)

        print(f"[{self.setNowTime()}] count 업데이트 완료")
        return posting_ok
    
    def _norm_type(self, t: str) -> str:
        return (t or "").strip()

    def _get_field(self, obj, default=None):
        # subject/content가 dict일 수도 있고 string일 수도 있으니 통합 처리
        if obj is None:
            return default
        return obj

    def _parse_subject(self, subject_obj) -> dict:
        """
        subject가
        - dict: {isUsing, text, isGenerate, size}
        - str : "철거 순서..."
        인 두 케이스를 모두 지원
        """
        if isinstance(subject_obj, dict):
            return {
                "isUsing": bool(subject_obj.get("isUsing", True)),
                "text": (subject_obj.get("text") or "").strip(),
                "isGenerate": bool(subject_obj.get("isGenerate", False)),
                "size": int(subject_obj.get("size", 80) or 80),
            }
        else:
            # 문자열이면 그냥 사용한다고 가정
            return {
                "isUsing": True,
                "text": (str(subject_obj) or "").strip(),
                "isGenerate": False,
                "size": 80,
            }

    def _parse_content(self, content_obj) -> dict:
        """
        content가
        - dict: {isUsing, text, isGenerate, size}
        - str : "직접 넣을 본문"
        인 두 케이스 지원
        """
        if isinstance(content_obj, dict):
            return {
                "isUsing": bool(content_obj.get("isUsing", True)),
                "text": (content_obj.get("text") or "").strip(),
                "isGenerate": bool(content_obj.get("isGenerate", True)),
                "size": int(content_obj.get("size", 800) or 800),
            }
        else:
            return {
                "isUsing": True,
                "text": (str(content_obj) or "").strip(),
                "isGenerate": False,
                "size": 800,
            }

    def _parse_links(self, links_obj) -> dict:
        """
        links가
        - {isUsing: bool, url: str}
        - 또는 {enabled: bool, items:[{text,url},...]} 같은 구조로 확장 가능
        """
        if not isinstance(links_obj, dict):
            return {"isUsing": False, "url": "", "items": []}

        # 1) 단일 url 형태
        is_using = bool(links_obj.get("isUsing", False))
        url = (links_obj.get("url") or "").strip()

        # 2) items 확장 형태(있으면 우선 사용)
        items = links_obj.get("items") or []
        enabled = bool(links_obj.get("enabled", False))

        return {
            "isUsing": is_using,
            "url": url,
            "enabled": enabled,
            "items": items,
        }
    def pick_random_extra_keyword(self, jobs_data: dict) -> str:
        items = jobs_data.get("extraKeywords", []) or []
        names = [x.get("name","").strip() for x in items if x.get("name")]
        return random.choice(names) if names else ""


    def render_campaign(self, region_name, job_name, campaign: dict):
        
        isCampaignSuccess = True

        # 0) 제목 만들기-----------------------------------------------------------------------------------
        # base_title = campaign.get("baseTitle", "")
        # title = f"{region_name} {job_name}"
        
        iframe = driver.find_element(By.ID, "mainFrame")
        driver.switch_to.frame(iframe)
        time.sleep(2)
        
        # if campaign.get("usingTitleGenerate"):
        #     r = gemini.get_title(base_title=title, job_name=job_name)
        #     print(f"[{self.setNowTime()}] gemini.get_title --!!")
        #     print(r)
        #     title = (r.get("title") or title).strip()

        title = (self.current_post_title or f"{region_name} {job_name}").strip()
        AddTitle.run(driver, title)
        
        # 2) 본문 섹션들------------------------------------------------------------------------------------------
        # for section in (campaign.get("content") or []):
        self.render_content(campaign, job_name=job_name)


        # 3) 전체 정렬------------------------------------------------------------------------------------------
        AlignAll.run(driver)
        
        # 4) 게시------------------------------------------------------------------------------------------
        # tags = campaign.get("hashTags", [])
        rr = gemini.get_hashTag(title=title, count=8)
        print(f"[{self.setNowTime()}] gemini.get_hashTag --!!")
        print(rr)
        tags_list = rr.get("tags") or []
        print(tags_list)

        addPostCheckCount = 0
        while True :

            AddPost.run(driver, tags_list)  
            time.sleep(5)
            errorStatus = self.checkError()

            if errorStatus == False :
                break
            if addPostCheckCount >= 3 :
                isCampaignSuccess = False
                break

            addPostCheckCount += 1

        return isCampaignSuccess
        
    def render_content(self, campaign: dict, job_name: str = ""):
        
        handles = driver.window_handles
        while True :
            if len(handles) >= 2 :
                break
            time.sleep(0.1)
        
        # driver.switch_to.window(driver.window_handles[1])
        # time.sleep(1)
        
        PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
        PROJECT_ROOT = os.path.dirname(PROJECT_ROOT)
        RESOURCE_DIR = os.path.join(PROJECT_ROOT, "resource")
    
        image_idx = random.randint(0, 1)

        main_image_path = os.path.join(RESOURCE_DIR, f"main_image_{image_idx}.jpg")
        hidden_image_path = os.path.join(RESOURCE_DIR, f"hidden_image_{image_idx}.jpg")

        if not os.path.exists(main_image_path):
            raise FileNotFoundError(main_image_path)

        if not os.path.exists(hidden_image_path):
            raise FileNotFoundError(hidden_image_path)

        print(f"[{self.setNowTime()}] [IMAGE] use index={image_idx}")
        print(f"[{self.setNowTime()}] main   : {main_image_path}")
        print(f"[{self.setNowTime()}] hidden : {hidden_image_path}")
        
        Common.focus_editor_end(driver)
        
        edited_main, edited_hidden, created_paths = editImage.edit_Image(main_image_path, hidden_image_path)
        try:
            AddImage.run(driver, edited_main)
            
            AddHiddenimage.run(driver, edited_hidden)
        finally:
            editImage.cleanup(created_paths)
        Common.focus_editor_end(driver)
        
        AddLink.run(driver, "tel:010-5536-9498")

        folder = self.pick_image_folder(job_name)
        all_imgs = self.list_images(folder)
        chosen = self.choose_up_to_5(all_imgs)

        print(f"[{self.setNowTime()}] [JOB-IMAGES] folder={folder}")
        print(f"[{self.setNowTime()}] [JOB-IMAGES] total={len(all_imgs)} chosen={len(chosen)}")
        
        full_text_parts = []
        total = len(chosen)
        for idx, img_path in enumerate(chosen, start=1):
            if not os.path.exists(img_path):
                continue
            edited_path = img_path
            created_paths = []

            try:
                edited_path, created_paths = editImage.edit_single(img_path, is_main=False)

                print(f"[{self.setNowTime()}] image path : {edited_path}")
                Common.focus_editor_end(driver)
                AddImage.run(driver, edited_path)

                if idx == 1:
                    print(f"[{self.setNowTime()}] 타이틀로 본문을 생성합니다!")
                    
                    rr = gemini.get_title_to_content(
                        title=self.current_post_title, 
                        size=300,
                        using_subject=False
                    )
                    print(f"[{self.setNowTime()}] gemini.get_title_to_content --!!")
                    print(rr)
                    body = (rr.get("body") or "").strip()
                    
                elif idx == total:
                    print(f"[{self.setNowTime()}] 본문으로 요약내용을 생성합니다!")
                    
                    full_text = "\n\n".join(full_text_parts)
                    rr = gemini.get_summary_section(
                        title=self.current_post_title,
                        full_text=full_text,
                        job_name=job_name,
                        size=300
                    )
                    print(f"[{self.setNowTime()}] gemini.get_summary_section --!!")
                    print(rr)
                    body = (rr.get("body") or "").strip()

                else:
                    print(f"[{self.setNowTime()}] 이미지로 본문을 생성합니다!")
                    subject = f"{job_name} 현장 사진 {idx}"
                    rr = gemini.get_image_section(
                        subject=subject,
                        image_paths=[edited_path],
                        size=280,
                        using_subject=True
                    )
                    print(f"[{self.setNowTime()}] gemini.get_image_section --!!")
                    print(rr)
                    body = (rr.get("body") or "").strip()
                    
                    
                if body:
                    print(body)
                    full_text_parts.append(body)
                    Common.focus_editor_end(driver)
                    AddText.run(driver, body)
                    
            finally:
                if created_paths:
                    editImage.cleanup(created_paths)


    
    def resource_root(self) -> str:
        project_root = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(project_root)
        return os.path.join(project_root, "resource")

    def pick_image_folder(self, job_name: str) -> str:
        """
        job_name에 포함된 폴더명이 있으면 그 폴더 사용
        없으면 all 사용
        """
        root = self.resource_root()

        candidates = [
            "물류센터철거",
            "사무실정리",
            "사무실처거",   # 오타 폴더명도 그대로
            "완파철거",
            "철거업체",
            "카페철거",
        ]

        # job_name에 폴더명이 포함되면 그 폴더 선택(첫 매칭)
        for folder in candidates:
            if folder in (job_name or ""):
                return os.path.join(root, folder)

        return os.path.join(root, "all")

    def list_images(self, folder_path: str) -> List[str]:
        exts = {".jpg", ".jpeg", ".png", ".webp"}
        if not os.path.isdir(folder_path):
            return []

        paths = []
        for name in os.listdir(folder_path):
            p = os.path.join(folder_path, name)
            if os.path.isfile(p) and os.path.splitext(name.lower())[1] in exts:
                paths.append(p)
        return paths

    def choose_up_to_5(self, paths: List[str]) -> List[str]:
        if not paths:
            return []
        if len(paths) <= 5:
            return paths
        return random.sample(paths, 5)

    def ensure_baseline_ip(self):
        if not self.base_ip:
            ip = self.get_ip()
            if not ip:
                raise RuntimeError("원래 IP 조회 실패 (get_ip가 빈값)")
            self.base_ip = ip
            print(f"[VPN] baseline ip saved = {self.base_ip}")
            
    def get_ip(self):
        urls = [
            "http://checkip.amazonaws.com",
            "https://api.ipify.org",
        ]
        for u in urls:
            try:
                r = requests.get(u, timeout=5)
                ip = r.text.strip()
                if ip:
                    return ip
            except:
                pass
        return ""
    
    def connect(
        self,
        country="kr",
        per_attempt_timeout=60,
        retry_delay=5,           
        stable_checks=2,       
        max_attempts=0           
    ) -> str:

        self.ensure_baseline_ip()
        before_ip = self.base_ip
        if not before_ip:
            raise RuntimeError("원래 IP(base_ip) 조회 실패")


        print(f"baseline ip = {before_ip}")

        attempt = 0
        while True:
            attempt += 1
            if max_attempts and attempt > max_attempts:
                raise TimeoutError(f"VPN 연결 실패: {max_attempts}회 재시도했지만 IP 변경 없음")

            print(f"connect attempt #{attempt}")

            if attempt > 1:
                self.disconnect(timeout=20)
                time.sleep(1)

            subprocess.Popen(
                [r"C:\Program Files\NordVPN\NordVPN.exe", "-c", country],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            start = time.time()
            consecutive = 0
            changed_ip = ""

            while time.time() - start < per_attempt_timeout:
                time.sleep(3)
                ip = self.get_ip()

                if not ip:
                    consecutive = 0
                    continue

                if ip != before_ip:
                    changed_ip = ip
                    consecutive += 1
                    print(f"detected different ip ({consecutive}/{stable_checks}) : {ip}")

                    if consecutive >= stable_checks:
                        print(f"CONNECTED. ip changed: {before_ip} -> {changed_ip}")
                        return changed_ip
                else:
                    consecutive = 0

            print(f"attempt #{attempt} timeout. IP not changed. retrying in {retry_delay}s...")
            time.sleep(retry_delay)
            
    def disconnect(self, timeout=60):
        try:
            self.ensure_baseline_ip()
            target = self.base_ip

            subprocess.Popen(
                [r"C:\Program Files\NordVPN\NordVPN.exe", "-d"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            start = time.time()
            stable = 0
            while time.time() - start < timeout:
                time.sleep(3)
                ip = self.get_ip()
                if not ip:
                    stable = 0
                    continue

                if ip == target:
                    stable += 1
                    if stable >= 2:
                        print(f"disconnected. back to baseline = {ip}")
                        return True
                else:
                    stable = 0

            print("disconnect timeout (baseline not restored)")
            return False
        except Exception as e:
            print(f"VPN 해제 중 오류 발생: {e}")
            return False



    # def connect(self):
    #     try:
    #         process = subprocess.Popen(
    #             ["C:\\Program Files\\NordVPN\\NordVPN.exe", "-c", "kr"],
    #             stdout=subprocess.PIPE,
    #             stderr=subprocess.PIPE,
    #             text=True
    #         )
    #         for line in process.stdout:
    #             print(line.strip())

    #         process.wait()
    #         print("VPN 연결 완료")
    #         time.sleep(10)

    #     except Exception as e:
    #         print(f"VPN 연결 중 오류 발생: {e}")
        
    def resetDriver(self):
        global driver
        try:
            if driver:
                print(f"[{self.setNowTime()}] 기존 드라이버 종료 시도")

                # 열린 모든 창을 닫기 전에 메인 창으로 포커스
                try:
                    driver.switch_to.window(driver.window_handles[0])
                except:
                    pass 

                for handle in driver.window_handles:
                    try:
                        driver.switch_to.window(handle)
                        driver.close()
                    except Exception as e:
                        print(f"[{self.setNowTime()}] 창 종료 중 오류: {e}")
                driver.quit()
                print(f"[{self.setNowTime()}] 드라이버 완전 종료 완료")
        except Exception as e:
            print(f"[{self.setNowTime()}] 드라이버 종료 중 예외: {e}")
        finally:
            print(f"[{self.setNowTime()}] 드라이버 재생성 시작")
            self.makeDriver()