import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import requests
from config import ZOTERO_BASE, ZOTERO_API_KEY


def _headers() -> dict:
    if ZOTERO_API_KEY:
        return {"Zotero-API-Key": ZOTERO_API_KEY}
    return {}


def get_item_key(citekey: str) -> str:
    resp = requests.get(
        f"{ZOTERO_BASE}/items",
        params={"q": citekey, "format": "json", "limit": 100},
        headers=_headers(),
    )
    resp.raise_for_status()
    for item in resp.json():
        extra = item.get("data", {}).get("extra", "")
        if f"Citation Key: {citekey}" in extra:
            return item["key"]
    raise ValueError(f"No Zotero item found for citekey: {citekey}")


def get_pdf_key(item_key: str) -> str:
    resp = requests.get(
        f"{ZOTERO_BASE}/items/{item_key}/children",
        params={"format": "json"},
        headers=_headers(),
    )
    resp.raise_for_status()
    for child in resp.json():
        if child.get("data", {}).get("contentType") == "application/pdf":
            return child["key"]
    raise ValueError(f"No PDF attachment found for item: {item_key}")


def get_annotations(pdf_key: str) -> list[dict]:
    resp = requests.get(
        f"{ZOTERO_BASE}/items/{pdf_key}/children",
        params={"format": "json"},
        headers=_headers(),
    )
    resp.raise_for_status()
    return [
        item["data"]
        for item in resp.json()
        if item.get("data", {}).get("itemType") == "annotation"
    ]
