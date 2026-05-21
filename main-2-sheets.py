import os
import re
import time
import logging
from datetime import datetime
from typing import List

import requests
import gspread
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google.oauth2.service_account import Credentials

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="Target Search Backend + Sheets", version="1.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UNIPILE_BASE_URL = os.getenv("UNIPILE_BASE_URL", "https://api20.unipile.com:15048/api/v1")
UNIPILE_API_KEY = os.getenv("UNIPILE_API_KEY", "GZ4Napww.06tYodoW/wclbYDfXer1uh0c0hwOt2JOaTz2b7spddg=")
UNIPILE_ACCOUNT_ID = os.getenv("UNIPILE_ACCOUNT_ID", "roVMOMXnT3GIbCSE6b-49Q")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID", "1R3DxBxZHG6hm432_mxVCXDZZhCU8bxtFbtTjFbR0--4")
GSHEET_CREDS_FILE = os.getenv("GSHEET_CREDS_FILE", "google_service_account.json")

MAX_PAGES = 90
MAX_TRIES = 5
RETRY_WAIT_S = 2
PAGE_INTERVAL_S = 7
BATCH_SIZE = 20
ACTIVE_COLUMNS = ["id", "full_name", "occupation", "location", "Linkedin URL", "Usernames"]


class SearchRequest(BaseModel):
    user_name: str = "Lead Search"
    locations: List[str] = []
    industries: List[str] = []
    professions: List[str] = []
    limit: int = 10
    max_pages: int = 5
    save_to_sheet: bool = True


def _headers() -> dict:
    return {
        "X-API-KEY": UNIPILE_API_KEY,
        "accept": "application/json",
        "Content-Type": "application/json",
    }


def _safe_sheet_name(name: str) -> str:
    name = re.sub(r"[[\]*?/\\:'`]", "", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name[:100] if name else "Lead Search"


def _unique_sheet_name(sh, desired: str) -> str:
    existing = [ws.title for ws in sh.worksheets()]
    if desired not in existing:
        return desired
    stamp = datetime.now().strftime("%m%d-%H%M")
    candidate = f"{desired[:90]} {stamp}"
    if candidate in existing:
        candidate = f"{desired[:85]} {datetime.now().strftime('%m%d-%H%M%S')}"
    return candidate


def resolve_parameter_ids(keywords: str, param_type: str, limit: int = 10) -> List[dict]:
    url = f"{UNIPILE_BASE_URL}/linkedin/search/parameters"
    params = {
        "account_id": UNIPILE_ACCOUNT_ID,
        "type": param_type,
        "keywords": keywords,
        "limit": limit,
    }
    try:
        resp = requests.get(url, headers=_headers(), params=params, timeout=20)
        resp.raise_for_status()
        return resp.json().get("items", [])
    except Exception as e:
        logger.warning(f"resolve {param_type} failed for '{keywords}': {e}")
        return []


def resolve_ids_for_list(values: List[str], param_type: str):
    resolved_ids = []
    unresolved = []
    for value in values:
        value = value.strip()
        if not value:
            continue
        items = resolve_parameter_ids(value, param_type, limit=5)
        if items:
            best_id = items[0].get("id")
            if best_id and best_id not in resolved_ids:
                resolved_ids.append(best_id)
        else:
            unresolved.append(value)
    return resolved_ids, unresolved


def build_keywords(professions: List[str], extra_keywords: List[str] = None) -> str:
    parts = [p.strip() for p in professions if p.strip()]
    if extra_keywords:
        parts.extend(k.strip() for k in extra_keywords if k.strip())
    seen = set()
    unique = []
    for item in parts:
        key = item.lower()
        if key not in seen:
            seen.add(key)
            unique.append(item)
    return " OR ".join(unique)


def search_linkedin(keywords: str, location_ids: List[str], industry_ids: List[str], limit: int, max_pages: int) -> List[dict]:
    url = f"{UNIPILE_BASE_URL}/linkedin/search"
    params = {"account_id": UNIPILE_ACCOUNT_ID}
    body = {
        "api": "classic",
        "category": "people",
        "limit": min(limit, 50),
    }

    if keywords:
        body["keywords"] = keywords
    if location_ids:
        body["location"] = location_ids
    if industry_ids:
        body["industry"] = industry_ids

    all_items = []
    cursor = None
    max_pages = min(max_pages, MAX_PAGES)

    for page in range(max_pages):
        if cursor:
            params["cursor"] = cursor

        data = None
        for attempt in range(MAX_TRIES):
            try:
                resp = requests.post(url, params=params, headers=_headers(), json=body, timeout=30)
                resp.raise_for_status()
                data = resp.json()
                break
            except Exception as e:
                logger.warning(f"search attempt {attempt + 1} failed: {e}")
                if attempt < MAX_TRIES - 1:
                    time.sleep(RETRY_WAIT_S)

        if not data:
            break

        items = data.get("items", [])
        if not items:
            break

        all_items.extend(items)
        cursor = data.get("cursor")

        if not cursor:
            break

        if page < max_pages - 1:
            time.sleep(PAGE_INTERVAL_S)

    return all_items


def map_profile(raw: dict) -> dict:
    profile_url = raw.get("profile_url") or raw.get("public_profile_url", "")
    name = raw.get("name") or raw.get("full_name", "")
    return {
        "id": raw.get("id", ""),
        "full_name": name,
        "occupation": raw.get("headline", ""),
        "location": raw.get("location", ""),
        "Linkedin URL": profile_url,
        "Usernames": raw.get("public_identifier", ""),
    }


def get_sheet_client():
    scopes = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = Credentials.from_service_account_file(GSHEET_CREDS_FILE, scopes=scopes)
    gc = gspread.authorize(creds)
    sh = gc.open_by_key(SPREADSHEET_ID)
    return gc, sh


def create_sheet_with_headers(sh, tab_name: str):
    safe_name = _safe_sheet_name(tab_name)
    unique_name = _unique_sheet_name(sh, safe_name)

    worksheet = sh.add_worksheet(title=unique_name, rows=1000, cols=len(ACTIVE_COLUMNS) + 2)
    worksheet.append_row(ACTIVE_COLUMNS)
    return worksheet, unique_name


def append_profiles_to_sheet(worksheet, profiles: List[dict]):
    rows = [[str(p.get(col, "") or "") for col in ACTIVE_COLUMNS] for p in profiles]
    for i in range(0, len(rows), BATCH_SIZE):
        batch = rows[i:i + BATCH_SIZE]
        worksheet.append_rows(batch, value_input_option="RAW")


@app.get("/")
def root():
    return {"status": "Target Search Backend + Sheets is running"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/resolve/locations")
def resolve_locations(q: str = Query(..., min_length=1)):
    results = resolve_parameter_ids(q.strip(), "LOCATION", limit=10)
    return {"items": [{"id": r.get("id"), "title": r.get("title", "")} for r in results]}


@app.get("/resolve/industries")
def resolve_industries(q: str = Query(..., min_length=1)):
    results = resolve_parameter_ids(q.strip(), "INDUSTRY", limit=10)
    return {"items": [{"id": r.get("id"), "title": r.get("title", "")} for r in results]}


@app.post("/search")
def search(req: SearchRequest):
    if "PASTE_YOUR_UNIPILE_API_KEY_HERE" in UNIPILE_API_KEY or "PASTE_YOUR_UNIPILE_ACCOUNT_ID_HERE" in UNIPILE_ACCOUNT_ID:
        raise HTTPException(status_code=500, detail="Please set your UNIPILE_API_KEY and UNIPILE_ACCOUNT_ID before running.")

    location_ids, unresolved_locs = resolve_ids_for_list(req.locations, "LOCATION")
    industry_ids, unresolved_inds = resolve_ids_for_list(req.industries, "INDUSTRY")
    keywords = build_keywords(req.professions, unresolved_locs + unresolved_inds)

    if not keywords and not location_ids and not industry_ids:
        raise HTTPException(status_code=400, detail="Please provide at least one location, industry, or profession.")

    raw_items = search_linkedin(
        keywords=keywords,
        location_ids=location_ids,
        industry_ids=industry_ids,
        limit=req.limit,
        max_pages=req.max_pages,
    )
    profiles = [map_profile(item) for item in raw_items]

    sheet_url = None
    tab_name = None
    sheet_error = None

    if req.save_to_sheet and profiles:
        try:
            _, sh = get_sheet_client()
            worksheet, tab_name = create_sheet_with_headers(sh, req.user_name)
            append_profiles_to_sheet(worksheet, profiles)
            sheet_url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}"
        except Exception as e:
            logger.error(f"Google Sheets save failed: {e}")
            sheet_error = str(e)

    return {
        "success": True,
        "count": len(profiles),
        "profiles": profiles,
        "sheet_url": sheet_url,
        "tab_name": tab_name,
        "sheet_error": sheet_error,
        "resolved": {
            "locations": location_ids,
            "industries": industry_ids,
            "keywords": keywords,
            "unresolved_locs": unresolved_locs,
            "unresolved_inds": unresolved_inds,
        },
    }
