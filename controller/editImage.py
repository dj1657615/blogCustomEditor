# controller/image_editor.py
# -*- coding: utf-8 -*-

import os
import uuid
import random
from pathlib import Path
from typing import Tuple, List, Optional

import cv2
import numpy as np
from PIL import Image, ExifTags



def _ensure_clean_dir(src_path: str | Path) -> Path:
    src_path = Path(src_path)
    parent = src_path.parent
    clean_dir = parent / "_clean"
    clean_dir.mkdir(parents=True, exist_ok=True)
    return clean_dir

def _unique_outpath(clean_dir: Path, stem: str, suffix: str = ".png") -> Path:
    token = uuid.uuid4().hex[:10]
    return clean_dir / f"{stem}_{token}{suffix}"

def _read_image_keep_exif_orientation(path: str | Path) -> np.ndarray:
    path = str(path)
    img = Image.open(path)

    try:
        exif = img._getexif()
        if exif:
            for tag, value in exif.items():
                if ExifTags.TAGS.get(tag, tag) == "Orientation":
                    if value == 3:
                        img = img.rotate(180, expand=True)
                    elif value == 6:
                        img = img.rotate(270, expand=True)
                    elif value == 8:
                        img = img.rotate(90, expand=True)
                    break
    except Exception:
        pass

    img = img.convert("RGBA")  
    arr = np.array(img)       
    
    arr = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGRA)
    return arr

def _save_png_no_metadata(arr_bgra: np.ndarray, out_path: str | Path) -> None:
    out_path = str(out_path)
    ok, enc = cv2.imencode(".png", arr_bgra, [cv2.IMWRITE_PNG_COMPRESSION, 9])
    if not ok:
        raise RuntimeError("PNG encode failed")

    with open(out_path, "wb") as f:
        f.write(enc.tobytes())

    try:
        img = Image.open(out_path)
        data = list(img.getdata())
        clean = Image.new(img.mode, img.size)
        clean.putdata(data)
        clean.save(out_path)  
    except Exception:
        pass

def _tiny_resize(arr_bgra: np.ndarray) -> np.ndarray:
    h, w = arr_bgra.shape[:2]
    scale = random.uniform(0.95, 1.0)

    new_w = max(2, int(round(w * scale)))
    new_h = max(2, int(round(h * scale)))

    # 너무 차이가 안 나면 1픽셀만 랜덤하게 조정
    if new_w == w and new_h == h:
        new_w = w + random.choice([-1, 1])
        new_h = h + random.choice([-1, 1])
        new_w = max(2, new_w)
        new_h = max(2, new_h)

    resized = cv2.resize(arr_bgra, (new_w, new_h), interpolation=cv2.INTER_AREA)
    return resized

def _apply_alpha(arr_bgra: np.ndarray) -> np.ndarray:
    if arr_bgra.shape[2] != 4:
        arr_bgra = cv2.cvtColor(arr_bgra, cv2.COLOR_BGR2BGRA)

    alpha_value = random.randint(240, 250)
    arr_bgra = arr_bgra.copy()
    arr_bgra[:, :, 3] = alpha_value
    return arr_bgra

def _subtle_border(arr_bgra: np.ndarray) -> np.ndarray:    
    
    if arr_bgra.shape[2] != 4:
        arr_bgra = cv2.cvtColor(arr_bgra, cv2.COLOR_BGR2BGRA)

    h, w = arr_bgra.shape[:2]
    thickness = random.randint(1, 3)

    # 가장자리 평균색
    top = arr_bgra[0:1, :, :3]
    bottom = arr_bgra[h-1:h, :, :3]
    left = arr_bgra[:, 0:1, :3]
    right = arr_bgra[:, w-1:w, :3]
    edge = np.concatenate([
        top.reshape(-1, 3), bottom.reshape(-1, 3),
        left.reshape(-1, 3), right.reshape(-1, 3)
    ], axis=0)
    mean_bgr = edge.mean(axis=0)

    noise = np.array([random.randint(-2,2), random.randint(-2,2), random.randint(-2,2)], dtype=np.float32)
    border_bgr = np.clip(mean_bgr + noise, 0, 255).astype(np.uint8)

    out = arr_bgra.copy()
    a = int(out[0, 0, 3])

    # 위/아래
    out[0:thickness, :, :3] = border_bgr
    out[h-thickness:h, :, :3] = border_bgr
    out[0:thickness, :, 3] = a
    out[h-thickness:h, :, 3] = a

    # 좌/우
    out[:, 0:thickness, :3] = border_bgr
    out[:, w-thickness:w, :3] = border_bgr
    out[:, 0:thickness, 3] = a
    out[:, w-thickness:w, 3] = a

    return out

def add_white_dots(arr_bgra: np.ndarray) -> np.ndarray:
    h, w = arr_bgra.shape[:2]
    out = arr_bgra.copy()

    y_min = int(h * 0.20)
    y_max = h - 1

    # 가장자리 너무 붙는 거 방지(너무 인위적이라)
    x_margin = max(5, int(w * 0.02))
    y_margin = max(5, int(h * 0.02))

    # 점 개수
    n_small = random.randint(6, 14)

    def rand_pos():
        x = random.randint(x_margin, w - 1 - x_margin)
        y = random.randint(max(y_min, y_margin), y_max - y_margin)
        return x, y

    def dot_color():
        v = random.randint(245, 255)       # 살짝 회색~흰색
        a = random.randint(220, 255)       # 알파도 랜덤(더 자연스럽게)
        return (v, v, v, a)                # BGRA

    def draw_dot(x, y, r):
        cv2.circle(out, (x, y), r, dot_color(), thickness=-1, lineType=cv2.LINE_AA)

    # 1) 작은 점들 위주
    for _ in range(n_small):
        x, y = rand_pos()

        p = random.random()
        if p < 0.85:
            r = random.randint(1, 3)      # 대부분 아주 작게
        else:
            r = random.randint(3, 5)      # 가끔 조금 크게

        draw_dot(x, y, r)

    # 2) "가끔" 중간 점 1개 추가 (확률 조절)
    # 예: 55% 확률로 한 개 추가
    if random.random() < 0.55:
        x, y = rand_pos()
        r = random.randint(5, 9)
        draw_dot(x, y, r)

    return out


def edit_Image(main_path: str | Path, hidden_path: str | Path) -> Tuple[str, str, List[str]]:
    main_path = Path(main_path)
    hidden_path = Path(hidden_path)

    # clean 폴더는 main 기준(둘이 같은 폴더면 동일)
    clean_dir = _ensure_clean_dir(main_path)

    created: List[str] = []

    # --- main ---
    main_arr = _read_image_keep_exif_orientation(main_path)
    main_arr = _tiny_resize(main_arr)          # 3)
    main_arr = _apply_alpha(main_arr)          # 2)
    main_arr = _subtle_border(main_arr)        # 4)
    main_arr = add_white_dots(main_arr)  # 5)

    main_out = _unique_outpath(clean_dir, "main", suffix=".png")
    main_final = _ensure_max_filesize(
        main_arr, main_out,
        max_bytes=16 * 1024 * 1024,
        max_side=2560,
        prefer_jpg=True
    )
    created.append(str(main_final))

    # --- hidden ---
    hidden_arr = _read_image_keep_exif_orientation(hidden_path)
    hidden_arr = _tiny_resize(hidden_arr)      # 3)
    hidden_arr = _apply_alpha(hidden_arr)      # 2)
    hidden_arr = _subtle_border(hidden_arr)    # 4)
    # hidden은 흰점 없음

    hidden_out = _unique_outpath(clean_dir, "hidden")
    _save_png_no_metadata(hidden_arr, hidden_out)
    created.append(str(hidden_out))

    return str(main_out), str(hidden_out), created

def edit_single(image_path: str | Path, *, is_main: bool = False) -> Tuple[str, List[str]]:
    image_path = Path(image_path)
    clean_dir = _ensure_clean_dir(image_path)

    created: List[str] = []

    arr = _read_image_keep_exif_orientation(image_path)
    arr = _tiny_resize(arr)
    arr = _apply_alpha(arr)
    arr = _subtle_border(arr)

    out = _unique_outpath(clean_dir, "img", suffix=".png")

    final_path = _ensure_max_filesize(
        arr,
        out,
        max_bytes=16 * 1024 * 1024,   # ✅ 16MB
        max_side=2560,                # ✅ 추천(안정성). 필요없으면 0
        prefer_jpg=True
    )

    created.append(str(final_path))
    return str(final_path), created

def cleanup(paths: List[str]) -> None:
    for p in paths or []:
        try:
            if p and os.path.exists(p):
                os.remove(p)
        except Exception:
            pass

def _ensure_max_filesize(
    arr_bgra: np.ndarray,
    out_path: Path,
    *,
    max_bytes: int = 16 * 1024 * 1024,  # 16MB
    max_side: int = 2560,               
    prefer_jpg: bool = True,
    max_rounds: int = 8
) -> None:
    if max_side and max_side > 0:
            h, w = arr_bgra.shape[:2]
            long_side = max(h, w)
            if long_side > max_side:
                scale = max_side / float(long_side)
                new_w = max(2, int(w * scale))
                new_h = max(2, int(h * scale))
                arr_bgra = cv2.resize(arr_bgra, (new_w, new_h), interpolation=cv2.INTER_AREA)

        # 1) 우선 PNG로 저장(현재 파이프라인 유지)
    _save_png_no_metadata(arr_bgra, out_path)

    if out_path.exists() and out_path.stat().st_size <= max_bytes:
        return out_path

    # 2) 그래도 크면(거의 없겠지만) → JPG로 전환 + 품질/해상도 다운
    bgr = cv2.cvtColor(arr_bgra, cv2.COLOR_BGRA2BGR)
    jpg_path = out_path.with_suffix(".jpg") if prefer_jpg else out_path

    quality = 90
    scale = 0.92

    for _ in range(max_rounds):
        h, w = bgr.shape[:2]
        new_w = max(320, int(w * scale))
        new_h = max(320, int(h * scale))
        bgr = cv2.resize(bgr, (new_w, new_h), interpolation=cv2.INTER_AREA)

        pil = Image.fromarray(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB))
        pil.save(jpg_path, "JPEG", quality=quality, optimize=True, subsampling=2)

        if jpg_path.exists() and jpg_path.stat().st_size <= max_bytes:
            # 원본 PNG 삭제(있으면)
            try:
                if out_path.exists() and out_path.suffix.lower() == ".png":
                    out_path.unlink()
            except Exception:
                pass
            return jpg_path

        quality = max(60, quality - 8)

    # 최후: 그냥 현재 파일 반환(그래도 대부분 여기까지 안 옴)
    return jpg_path if jpg_path.exists() else out_path

