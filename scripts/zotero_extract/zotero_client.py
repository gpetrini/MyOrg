import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import requests
from config import ZOTERO_BASE, ZOTERO_API_KEY

BBT_RPC = "http://localhost:23119/better-bibtex/json-rpc"


def _headers() -> dict:
    if ZOTERO_API_KEY:
        return {"Zotero-API-Key": ZOTERO_API_KEY}
    return {}


def get_item_key(citekey: str) -> str:
    resp = requests.post(
        BBT_RPC,
        json={"jsonrpc": "2.0", "method": "item.search", "params": [citekey]},
    )
    resp.raise_for_status()
    result = resp.json()
    if "error" in result or not result.get("result"):
        raise ValueError(f"No Zotero item found for citekey: {citekey}")
    return result["result"][0]["id"].split("/")[-1]


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
        params={"format": "json", "itemType": "annotation"},
        headers=_headers(),
    )
    resp.raise_for_status()
    return [item["data"] for item in resp.json()]
