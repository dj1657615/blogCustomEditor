import os
import gspread
from datetime import datetime, timedelta
from google.oauth2.service_account import Credentials

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SERVICE_ACCOUNT_JSON = os.path.join(BASE_DIR, "service_account.json")

SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1ufNGhXrpmRowcmBDMOtR7X_8x6fjW8ZvrF36eKB1x3o/edit#gid=0"

ACCOUNT_SHEET_NAME = "account"
POST_SHEET_NAME = "post"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

def open_ws(worksheet_name: str):
    creds = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_JSON,
        scopes=SCOPES
    )
    gc = gspread.authorize(creds)
    sh = gc.open_by_url(SPREADSHEET_URL)
    return sh.worksheet(worksheet_name)

def get_account_ws():
    return open_ws(ACCOUNT_SHEET_NAME)

def header_map(ws):
    headers = ws.row_values(1)
    return {h.strip(): i + 1 for i, h in enumerate(headers) if h and h.strip()}

def _to_int(v, default=0):
    try:
        s = str(v).strip()
        return int(s) if s != "" else default
    except:
        return default

def _parse_used_date(s: str):
    """
    used_date 파싱 (여러 포맷 허용)
    - 비어있으면 None
    """
    if s is None:
        return None
    s = str(s).strip()
    if not s:
        return None

    # 많이 쓰는 포맷들
    fmts = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
        "%Y.%m.%d %H:%M:%S",
        "%Y.%m.%d %H:%M",
        "%Y.%m.%d",
    ]
    for f in fmts:
        try:
            return datetime.strptime(s, f)
        except:
            pass
    return None  # 파싱 실패


# ---------------------------------------------------- account------------------------------------------------------------------------------------
# ---------- 1) 계정 가져오기 ----------
def get_account_min_count_with_cooldown(
    *,
    cooldown_hours=3,
):
    account_ws = get_account_ws()

    now = datetime.now()
    cutoff = now - timedelta(hours=cooldown_hours)

    rows = account_ws.get_all_records()
    candidates = []

    for sheet_row, r in enumerate(rows, start=2):
        status = str(r.get("status", "")).strip()
        
        if status != "":
            continue

        cnt = _to_int(r.get("count", ""), 0)

        used_dt = _parse_used_date(r.get("used_date", ""))
        if used_dt is not None and used_dt > cutoff:
            continue

        r["row"] = sheet_row
        r["count_int"] = cnt
        candidates.append(r)

    if not candidates:
        return None

    candidates.sort(key=lambda x: x["count_int"])
    min_count = candidates[0]["count_int"]

    for c in candidates:
        if c["count_int"] == min_count:
            return c

    return None


# ---------- 2) 로그인 실패 시 status 업데이트 ----------
def update_account_status(row: int, status_value: str):
    account_ws = get_account_ws()
    col = header_map(account_ws)
    account_ws.update_cell(row, col["status"], status_value)


# ---------- 3) 사용 후 count +1, used_date 현재시각 업데이트 ----------
def mark_account_used(
    row: int,
    *,
    date_fmt="%Y-%m-%d %H:%M:%S",
    also_status=None
):
    account_ws = get_account_ws()
    col = header_map(account_ws)

    updates = []

    if "count" in col:
        cur = account_ws.cell(row, col["count"]).value
        updates.append(
            gspread.Cell(row, col["count"], _to_int(cur, 0) + 1)
        )

    if "used_date" in col:
        updates.append(
            gspread.Cell(row, col["used_date"], datetime.now().strftime(date_fmt))
        )

    if also_status is not None and "status" in col:
        updates.append(
            gspread.Cell(row, col["status"], also_status)
        )

    if updates:
        account_ws.update_cells(updates, value_input_option="USER_ENTERED")
        
# ---------------------------------------------------- post------------------------------------------------------------------------------------

def append_post_log(published_date: str, title: str, url: str, account_id: str):
    
    post_ws = open_ws(POST_SHEET_NAME)
    post_ws.append_row(
        [published_date, title, url, account_id],
        value_input_option="USER_ENTERED"
    )