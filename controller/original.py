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
        
        print("\n" + "~~" * 100)
        print("loop start!!")
        self.makeDriver()

        while True :
            
            print("\n" + "=" * 70)
            
            campaigns = self.load_campaigns("campaign.json")
            print(campaigns[0])
            
            if not campaigns:
                print("❌ 사용 가능한 캠페인이 없습니다.")
                return

            
            while True :
                acc = googleSheet.get_account_min_count_with_cooldown(
                    cooldown_hours=3,
                    status_exclude=("BLOCK", "LOGIN_FAIL"),
                    require_status_empty=False
                )
                print(f"Google Sheet Account Data : {acc}")
                
                if not acc:
                    print("❌ 사용 가능한 계정이 없습니다.")
                    return
                
                self.naver_id = acc["id"]
                self.naver_pw = acc["pw"]
                row = acc["row"]
                
                # loginResult = self.login(row)
                
                # if loginResult :
                #     time.sleep(2)
                #     break
                break
            self.blog_id = GetMyBlogId.run(driver, self.BLOG_URL)
            
            MoveWritePage.run(driver, self.blog_id)
            
            before_handles = driver.window_handles
            driver.execute_script("window.open('', '_blank');")
            time.sleep(1)
            after_handles = driver.window_handles
            new_handle = list(set(after_handles) - set(before_handles))[0]
            driver.switch_to.window(new_handle)
            MoveWritePage.run(driver, self.blog_id)
            original_handle = driver.window_handles[0]  
            driver.switch_to.window(original_handle)

            self.doPosting(campaigns[0])

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
    
    def doPosting(self, data) :
        print("posting start")
        
        try:
            region_name, job_name, regions_data, jobs_data = Common.pick_region_job(top_k=50)
        except Exception as e:
            print(f"지역/작업 선택 실패: {e}")
            return

        title = f"{region_name} {job_name}"
        self.current_post_title = title
        print(f"최종 제목: {title}")


        self.render_campaign(region_name, job_name, data)


        # count +1
        Common.increment_count_by_name(regions_data["regions"], region_name, inc=1)
        Common.increment_count_by_name(jobs_data["jobs"], job_name, inc=1)

        # 저장
        Common.save_json("regions.json", regions_data)
        Common.save_json("jobs.json", jobs_data)

        print("count 업데이트 완료")

    
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
        
    def render_campaign(self, region_name, job_name, campaign: dict):
        
        # 0) 제목 만들기-----------------------------------------------------------------------------------
        # base_title = campaign.get("baseTitle", "")
        title = f"{region_name} {job_name}"

        if campaign.get("usingTitleGenerate"):
            r = gemini.get_title(base_title=title, keywords=job_name)
            title = (r.get("title") or title).strip()

        self.current_post_title = title
        AddTitle.run(driver, title)
        
        # 2) 본문 섹션들------------------------------------------------------------------------------------------
        for section in (campaign.get("content") or []):
            self.render_content(driver, campaign, section, job_name=job_name)

        # 4) 게시------------------------------------------------------------------------------------------
        # tags = campaign.get("hashTags", [])
        rr = gemini.get_hashTag(title=title, count=8)
        tags_list = rr.get("tags") or []
        tags_str = " ".join(tags_list)

        AddPost.run(driver, tags_str)  

        # 1) 서론------------------------------------------------------------------------------------------
        # if campaign.get("usingWelcomeContent") and (campaign.get("welcome", {}).get("generate", True)):
        #     w = campaign.get("welcome", {})
        #     rr = gemini.get_welcome(
        #         campaign_name=campaign.get("name", ""),
        #         title=title,
        #         size=int(w.get("size", 400) or 400),
        #         tone=w.get("tone", "친근한 반말"),
        #     )
        #     welcome_text = (rr.get("body") or "").strip()
        #     if welcome_text:
        #         AddText.run(driver, welcome_text)

        # 3) 결론
        # if campaign.get("usingEndingContent") and (campaign.get("ending", {}).get("generate", True)):
        #     e = campaign.get("ending", {})
        #     rr = gemini.generate(
        #         "ending_generate",
        #         campaign_name=campaign.get("name", ""),
        #         base_title=title,
        #         size=int(e.get("size", 350) or 350),
        #     )
        #     ending_text = (rr.get("body") or rr.get("text") or "").strip()
        #     if ending_text:
        #         AddText.run(driver, ending_text)

    def render_content(self, driver, campaign: dict, section: dict, job_name: str = ""):
        
        handles = driver.window_handles
        while True :
            if len(handles) >= 2 :
                break
            time.sleep(0.1)
        
        driver.switch_to.window(driver.window_handles[1])
        time.sleep(1)
        
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

        print(f"[IMAGE] use index={image_idx}")
        print(f"  main   : {main_image_path}")
        print(f"  hidden : {hidden_image_path}")
        
        Common.focus_editor_end()
        
        edited_main, edited_hidden, created_paths = editImage.edit_Image(main_image_path, hidden_image_path)
        try:
            AddImage.run(driver, edited_main)
            AddHiddenimage.run(driver, edited_hidden)
        finally:
            editImage.cleanup(created_paths)
        Common.focus_editor_end()
        
        AddLink.run(driver, "tel:010-5536-9498")

        folder = self._pick_image_folder(job_name)
        all_imgs = self._list_images(folder)
        chosen = self._choose_up_to_5(all_imgs)

        print(f"[JOB-IMAGES] folder={folder}")
        print(f"[JOB-IMAGES] total={len(all_imgs)} chosen={len(chosen)}")
        
        total = len(chosen)
        for idx, img_path in enumerate(chosen, start=1):
            if not os.path.exists(img_path):
                continue
            
            edited_path = img_path
            created_paths = []

            try:
                edited_path, created_paths = editImage.edit_single(img_path, is_main=False)

                Common.focus_editor_end()
                AddImage.run(driver, edited_path)

                if idx == 1:
                    rr = gemini.get_title_to_content(
                        title=f"{self.current_post_title}",   
                        size=900
                    )
                    body = (rr.get("body") or "").strip()
                    
                    
                elif idx == total:
                    rr = gemini.get_summary_section(
                        subject=f"{job_name} 작업 요약",
                        size=600,
                        using_subject=True
                    )
                    body = (rr.get("body") or "").strip()

                else:
                    subject = f"{job_name} 현장 사진 {idx}"
                    rr = gemini.get_image_section(
                        subject=subject,
                        image_urls=[edited_path],   
                        size=700,
                        using_subject=True
                    )
                    body = (rr.get("body") or "").strip()
                    
                    
                if body:
                    Common.focus_editor_end()
                    AddText.run(driver, body)
                    
            finally:
                if created_paths:
                    editImage.cleanup(created_paths)
                    

        
    def render_content_original(self, driver, campaign: dict, section: dict, job_name: str = ""):
        s_type = section.get("type")

        # hiddenImage는 글에 넣지 않음(원하면 여기서 다운로드/분석만)
        if s_type == "hiddenImage":
            return

        resources = section.get("resources") or []

        subject_cfg = self._parse_subject(section.get("subject"))
        content_cfg = self._parse_content(section.get("content"))
        links_cfg = self._parse_links(section.get("links"))

        # A) subject 처리
        subject_text = ""
        if subject_cfg["isUsing"]:
            subject_text = subject_cfg["text"]

            # 소제목 생성 옵션
            if subject_cfg["isGenerate"] and subject_text:
                rr = gemini.generate("subtitle_to_content_generate", subject=subject_text, size=subject_cfg["size"])
                subject_text = (rr.get("subject") or rr.get("title") or subject_text).strip()

            if subject_text:
                Common.focus_editor_end()
                AddIndexTitle.run(driver, subject_text)

        # B) 본문(content) 처리
        body_text = ""
        if content_cfg["isUsing"]:
            # 1) 직접 텍스트가 있으면 그걸 사용
            if content_cfg["text"]:
                body_text = content_cfg["text"]

            # 2) 비어있고 isGenerate면 gemini 생성
            elif content_cfg["isGenerate"]:
                size = content_cfg["size"]
                using_subject = True 
                
                if "usingSubject" in section:
                    using_subject = bool(section.get("usingSubject", True))

                # 타입별 생성 라우팅
                if s_type in ("image", "imageContent"):
                    rr = gemini.get_image_section(
                        subject=subject_text,
                        image_urls=resources,
                        size=size,
                        using_subject=using_subject
                    )
                    body_text = (rr.get("body") or "").strip()

                elif s_type == "summary":
                    rr = gemini.get_summary_section(
                        subject=subject_text,
                        size=size,
                        using_subject=using_subject
                    )
                    body_text = (rr.get("body") or "").strip()

                else:
                    rr = gemini.get_paragraph_section(
                        subject=subject_text,
                        size=size,
                        using_subject=using_subject
                    )
                    body_text = (rr.get("body") or "").strip()

        # C) 이미지 넣기
        if s_type in ("image", "imageContent") and resources:
            for url in resources:
                Common.focus_editor_end()
                AddImage.run(driver, url)

        # D) 본문 넣기
        if body_text:
            Common.focus_editor_end()
            AddText.run(driver, body_text)

        # E) 링크 넣기
        if links_cfg.get("isUsing") and links_cfg.get("url"):
            link_text = subject_text or "관련 링크"
            Common.focus_editor_end()
            AddLink.run(driver, link_text, links_cfg["url"])


    #ㅇㅁ닝ㅁㄴ임ㄴ임니임닝ㅁ니임ㄴ임ㄴ임닝ㄴ미임ㄴ임닝민임ㄴㅇ
    def _resource_root(self) -> str:
        project_root = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(project_root)
        return os.path.join(project_root, "resource")

    def _pick_image_folder(self, job_name: str) -> str:
        """
        job_name에 포함된 폴더명이 있으면 그 폴더 사용
        없으면 all 사용
        """
        root = self._resource_root()

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

    def _list_images(self, folder_path: str) -> List[str]:
        exts = {".jpg", ".jpeg", ".png", ".webp"}
        if not os.path.isdir(folder_path):
            return []

        paths = []
        for name in os.listdir(folder_path):
            p = os.path.join(folder_path, name)
            if os.path.isfile(p) and os.path.splitext(name.lower())[1] in exts:
                paths.append(p)
        return paths

    def _choose_up_to_5(self, paths: List[str]) -> List[str]:
        if not paths:
            return []
        if len(paths) <= 5:
            return paths
        return random.sample(paths, 5)