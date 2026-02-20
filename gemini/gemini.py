# -*- coding: utf-8 -*-
import random
import re
import os, json, time, mimetypes
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
import google.generativeai as genai
from google.generativeai import types

import mimetypes

from gemini.prompts import (
    title_generate,
    welcome_generate,
    ending_generate,

    title_to_content_generate,
    image_to_content_generate,
    subtitle_to_content_generate,
    summary_generate,
    
    hashtag_generate,
)

FORBIDDEN_WORDS = ["시불", "고자", "노출", "호로", "엉덩이", "만족", "의사", "진단"]

PYEONG_LIST_30 = [
    "25평", "30평", "24평", "26평", "32평",
    "20평", "28평", "34평", "27평", "23평",
    "18평", "21평", "36평", "22평", "29평",
    "33평", "35평", "19평", "38평", "17평",
    "40평", "16평", "31평", "37평", "39평",
    "15평", "14평", "42평", "45평", "50평",
]
picked_pyeong = random.choice(PYEONG_LIST_30)
print("선택된 평수:", picked_pyeong)


GEMINI_API_KEYS = [
    "AIzaSyASLFah067gAaDBtQHok4VcpgaQjPhVM-s",
    "AIzaSyDbW9WJkdvXYdBZYZvriAcDySX2wYQRBkE",
    "AIzaSyCWXts6UsXw96wxng0zVaCEAk2vdPIwhxI",
    "AIzaSyBZJ8_OOxtpsJfYQHckJJEUYFKjZ9x1igs",
    "AIzaSyDbW9WJkdvXYdBZYZvriAcDySX2wYQRBkE",
    "AIzaSyAHex5Am8YEg4tEmHK_yZGXB6jN0Ext7BQ",
]

MODEL_VERSION_DEFAULT = "gemini-2.5-flash"

def is_ratelimit_error( e: Exception) -> bool:
    msg = (str(e) or "").lower()

    keywords = [
        "resource_exhausted",
        "quota",
        "exceeded",
        "rate limit",
        "too many requests",
        "429",
        "insufficient quota",
        "quota exceeded",
    ]
    return any(k in msg for k in keywords)


def is_transient_error( e: Exception) -> bool:
    msg = (str(e) or "").lower()
    keywords = [
        "timeout",
        "timed out",
        "deadline",
        "temporarily",
        "unavailable",
        "internal",
        "503",
        "500",
        "connection",
        "reset",
        "broken pipe",
    ]
    return any(k in msg for k in keywords)


class GeminiKeyPool:
    def __init__(self, keys: List[str]):
        self.keys = [k for k in keys if k and k.strip()]
        if not self.keys:
            raise ValueError("GEMINI_API_KEYS가 비어있습니다.")
        self.idx = 0

    def current_key(self) -> str:
        return self.keys[self.idx]

    def rotate(self) -> str:
        self.idx = (self.idx + 1) % len(self.keys)
        return self.current_key()


_KEYPOOL = GeminiKeyPool(GEMINI_API_KEYS)


def text_to_json(resp) -> str:
    text = None
    try:
        t = getattr(resp, "text", None)   
        if t is not None:
            text = resp.text              
    except Exception:
        text = None

    if not text:
        chunks = []
        for c in (getattr(resp, "candidates", []) or []):
            content = getattr(c, "content", None)
            if not content:
                continue
            for part in (getattr(content, "parts", []) or []):
                # text 파트
                t = getattr(part, "text", None)
                if t:
                    chunks.append(t)
                data = getattr(part, "inline_data", None)
                if data and getattr(data, "data", None):
                    try:
                        chunks.append(data.data.decode("utf-8"))
                    except Exception:
                        pass
        text = "\n".join(chunks).strip()

    if not text:
        return "{}"

    s = text.strip()
    if s.startswith("```json"):
        s = s.removeprefix("```json").removesuffix("```").strip()
    elif s.startswith("```"):
        s = s.removeprefix("```").removesuffix("```").strip()

    return s


def extract_json_object(s: str) -> str:
    if not s:
        return ""
    s = s.strip()
    s = re.sub(r"^```(?:json)?\s*", "", s)
    s = re.sub(r"\s*```$", "", s)
    start = s.find("{")
    end = s.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return ""
    return s[start:end + 1]


def call_gemini_json(prompt: str, model_version: str, max_retries: int = 3) -> Dict[str, Any]:
    last_err: Optional[Exception] = None

    for attempt in range(1, max_retries + 1):
        api_key = _KEYPOOL.current_key()
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(model_version)

            response = model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "top_k": 40,
                    "max_output_tokens": 20000,
                    "response_mime_type": "application/json",
                },
            )

            raw = text_to_json(response)
            if not raw or raw.strip() in ("", "{}", "null"):
                return {}

            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                fixed = extract_json_object(raw)
                if fixed:
                    return json.loads(fixed)
                # 그래도 안 되면 실패로 보고 재시도
                raise

        except Exception as e:
            last_err = e

            if is_ratelimit_error(e):
                new_key = _KEYPOOL.rotate()
                print(f"[Gemini] quota/rate-limit 감지 → KEY rotate (attempt={attempt}/{max_retries})")
                time.sleep(0.3 + random.random() * 0.7)
                continue

            if is_transient_error(e):
                sleep_s = min(8.0, (2 ** (attempt - 1)) + random.random())
                print(f"[Gemini] transient error → retry after {sleep_s:.2f}s (attempt={attempt}/{max_retries})")
                time.sleep(sleep_s)
                continue

            print(f"[Gemini] non-retryable error: {repr(e)}")
            break

    print(f"[Gemini] FAILED after {max_retries} attempts. last_error={repr(last_err)}")
    return {}


def call_gemini_json_with_images(prompt: str, image_paths: List[str], model_version: str, max_retries: int = 3) -> Dict[str, Any]:
    last_err: Optional[Exception] = None

    for attempt in range(1, max_retries + 1):
        api_key = _KEYPOOL.current_key()
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(model_version)

            parts = [prompt]

            # ✅ 이미지 파일 업로드 후, 업로드된 파일 객체를 parts에 넣기
            for p in image_paths:
                uploaded = genai.upload_file(p)
                parts.append(uploaded)

            response = model.generate_content(
                parts,
                generation_config={
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "top_k": 40,
                    "max_output_tokens": 20000,
                    "response_mime_type": "application/json",
                },
            )

            raw = text_to_json(response)
            if not raw or raw.strip() in ("", "{}", "null"):
                return {}

            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                fixed = extract_json_object(raw)
                if fixed:
                    return json.loads(fixed)
                raise

        except Exception as e:
            last_err = e
            if is_ratelimit_error(e):
                _KEYPOOL.rotate()
                time.sleep(0.3 + random.random() * 0.7)
                continue
            if is_transient_error(e):
                sleep_s = min(8.0, (2 ** (attempt - 1)) + random.random())
                time.sleep(sleep_s)
                continue

            print(f"[Gemini] non-retryable error: {repr(e)}")
            break

    print(f"[Gemini] FAILED(with_images) after {max_retries} attempts. last_error={repr(last_err)}")
    return {}

PROMPT_BUILDERS: Dict[str, Callable[..., str]] = {

    "title_generate": title_generate.get_prompt,
    "welcome_generate": welcome_generate.get_prompt,
    "ending_generate": ending_generate.get_prompt,

    "image_to_content_generate": image_to_content_generate.get_prompt,
    "title_to_content_generate": title_to_content_generate.get_prompt,
    "subtitle_to_content_generate": subtitle_to_content_generate.get_prompt,
    "summary_generate": summary_generate.get_prompt,
    
    "hashtag_generate": hashtag_generate.get_prompt,
}

def generate(kind: str, model_version: str = MODEL_VERSION_DEFAULT, images: Optional[List[str]] = None, **kwargs) -> Dict[str, Any]:
    builder = PROMPT_BUILDERS.get(kind)
    if not builder:
        raise ValueError(f"Unknown prompt kind: {kind}")

    prompt = builder(**kwargs)

    if images:
        return call_gemini_json_with_images(prompt, images, model_version=model_version)

    return call_gemini_json(prompt, model_version=model_version)



def get_title(region: str, main_keyword: str, pools: dict) -> Dict[str, Any]:
    return generate(
        "title_generate",
        region=region,
        main_keyword=main_keyword,
        pools=pools,
    )
    
def get_welcome(campaign_name: str, title: str, size: int = 400, tone: str = "친근한 반말") -> Dict[str, Any]:
    return generate("welcome_generate", campaign_name=campaign_name, title=title, size=size, tone=tone)

def get_ending(campaign_name: str, title: str, size: int = 350) -> Dict[str, Any]:
    return generate("ending_generate", campaign_name=campaign_name, title=title, size=size)

def get_hashTag(title: str, count: int = 8) -> Dict[str, Any]:
    return generate("hashtag_generate", title=title, count=count)


def get_image_section(
    subject: str,
    image_paths: List[str],
    size: int = 280,
    using_subject: bool = True
) -> Dict[str, Any]:
    return generate(
        "image_to_content_generate",
        subject=subject,
        size=size,
        using_subject=using_subject,
        images=image_paths, 
        forbidden_words=FORBIDDEN_WORDS
    )
    
def get_title_to_content(title: str, size: int = 300, using_subject: bool = True) -> Dict[str, Any]:
    return generate(
        "title_to_content_generate",
        title=title,          
        size=size,
        using_subject=using_subject,
        forbidden_words=FORBIDDEN_WORDS #
    )

def get_summary_section(title: str, full_text: str, job_name: str = "", size: int = 300) -> Dict[str, Any]:
    return generate(
        "summary_generate",
        title=title,
        full_text=full_text,
        job_name=job_name,
        size=size,
        forbidden_words=FORBIDDEN_WORDS #
    )