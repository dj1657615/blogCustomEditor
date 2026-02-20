# -*- coding: utf-8 -*-
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
from typing import Dict, Any, List, Optional

import json, time, traceback, re, clipboard, random, pyautogui, ctypes,os

def copyAndInput(value, element) :
    clipboard.copy(value)
    time.sleep(0.5)
    field = element
    field.send_keys(Keys.CONTROL + "v")
    time.sleep(0.5)

def ActionEnter(driver) :
    ActionChains(driver).send_keys(Keys.ENTER).perform()
    time.sleep(0.2)

def focus_editor_end(driver):
    bottom = driver.find_element(By.CLASS_NAME, "se-canvas-bottom")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", bottom)
    time.sleep(0.2)
    bottom.click()
    time.sleep(0.2)
    
def pick_region_job(top_k=50):
    regions_data = load_json("regions.json")
    jobs_data = load_json("jobs.json")

    regions = regions_data.get("regions", [])
    jobs = jobs_data.get("jobs", [])

    if not regions:
        raise ValueError("regions.json regions 비어있음")
    if not jobs:
        raise ValueError("jobs.json jobs 비어있음")

    picked_region = pick_least_used_random(regions, top_k=top_k)
    picked_job = pick_least_used_random(jobs, top_k=top_k)

    region_name = picked_region["name"]
    job_name = picked_job["name"]

    print(f"선택된 지역: {region_name} (count={picked_region.get('count',0)})")
    print(f"선택된 작업: {job_name} (count={picked_job.get('count',0)})")

    return region_name, job_name, regions_data, jobs_data

def find_project_root(start: Path = None) -> Path:
    if start is None:
        start = Path(__file__).resolve()

    for p in [start.parent] + list(start.parents):
        if (p / "region.json").exists() and (p / "job.json").exists():
            return p
    return Path(__file__).resolve().parents[1]

PROJECT_ROOT = find_project_root()

def load_json(filename: str) -> dict:
    path = PROJECT_ROOT / filename
    print(f"[load_json] try open: {path}")
    if not path.exists():
        print(f"[load_json] ❌ file not found: {path}")
        return {}
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"[load_json] ✅ keys: {list(data.keys())}")
        return data
    except Exception as e:
        print(f"[load_json] ❌ JSON parse error: {e}")
        return {}


def save_json(filename: str, data: dict) -> None:
    path = PROJECT_ROOT / filename
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def pick_least_used_random( items: List[dict], top_k: int = 30) -> dict:
    """
    items: [{"name": "...", "count": 0}, ...]
    - count 오름차순 정렬
    - 상위 top_k 중 랜덤 1개 반환
    """
    if not items:
        raise ValueError("items empty")

    # count 안전 처리
    def c(x):
        try:
            return int(x.get("count", 0))
        except Exception:
            return 0

    items_sorted = sorted(items, key=c)
    pool = items_sorted[:max(1, min(top_k, len(items_sorted)))]
    return random.choice(pool)

    
def increment_count_by_name( items: List[dict], name: str, inc: int = 1) -> bool:
    """
    items 내에서 name 찾아 count += inc
    찾으면 True, 못찾으면 False
    """
    for it in items:
        if it.get("name") == name:
            try:
                it["count"] = int(it.get("count", 0)) + inc
            except Exception:
                it["count"] = inc
            return True
    return False


def filter_min_count_items(items: List[dict]) -> List[dict]:
    """
    items: [{"name": "...", "count": 0}, ...]
    - count 최소값을 가진 항목들만 반환
    """
    if not items:
        return []

    def c(x):
        try:
            return int(x.get("count", 0))
        except Exception:
            return 0

    min_c = min(c(x) for x in items)
    return [x for x in items if c(x) == min_c]


def build_pools_min_count(jobs_data: Dict[str, Any]) -> Dict[str, List[str]]:
    def names_min_or_all(key: str) -> List[str]:
        full = jobs_data.get(key, []) or []
        if not full:
            return []
        mins = filter_min_count_items(full)
        chosen = mins if mins else full
        return [x.get("name", "") for x in chosen if x.get("name")]

    return {
        "subKeywords": names_min_or_all("subKeywords"),
        "targets": names_min_or_all("targets"),
        "workSites": names_min_or_all("workSites"),
        "expandKeywords": names_min_or_all("expandKeywords"),
        "extraKeywords": names_min_or_all("extraKeywords"),
    }
    

def increment_used_counts( regions_data: dict, jobs_data: dict, picked: dict):
    # 1) 지역
    increment_count_by_name(regions_data["regions"], picked["region"], inc=1)

    # 2) 메인키워드(jobs)
    increment_count_by_name(jobs_data["jobs"], picked["main"], inc=1)

    # 3) 나머지 카테고리들
    if picked.get("subKeyword"):
        increment_count_by_name(jobs_data["subKeywords"], picked["subKeyword"], inc=1)
    if picked.get("target"):
        increment_count_by_name(jobs_data["targets"], picked["target"], inc=1)
    if picked.get("workSite"):
        increment_count_by_name(jobs_data["workSites"], picked["workSite"], inc=1)
    if picked.get("expandKeyword"):
        increment_count_by_name(jobs_data["expandKeywords"], picked["expandKeyword"], inc=1)

    # extraKeyword는 "사용됐다면"만 +1
    extra = picked.get("extraKeyword", "").strip()
    if extra:
        increment_count_by_name(jobs_data["extraKeywords"], extra, inc=1)

