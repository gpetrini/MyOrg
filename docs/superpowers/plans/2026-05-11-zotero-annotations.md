# Zotero Annotations Extractor — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Python CLI that extracts PDF annotations from the Zotero local REST API and inserts them into the correct sections of an existing Org-mode bib file.

**Architecture:** Four files: `config.py` holds routing dictionaries; `zotero_client.py` wraps the Zotero local REST API at `localhost:23119`; `org_writer.py` handles file search by `#+reference:` and section insertion; `extract_zotero.py` is the CLI entry point. Citekey is always required (used for Zotero lookup); `--file` overrides automatic org file search.

**Tech Stack:** Python 3.10+, `requests`, `pytest`

---

## File Map

| File | Responsibility |
|------|---------------|
| `scripts/zotero_extract/config.py` | Codetag-to-section mapping and constants |
| `scripts/zotero_extract/zotero_client.py` | Zotero local REST API calls |
| `scripts/zotero_extract/org_writer.py` | File search, codetag parsing, section insertion |
| `scripts/zotero_extract/extract_zotero.py` | CLI entry point and orchestration |
| `scripts/zotero_extract/requirements.txt` | Python dependencies |
| `tests/zotero_extract/__init__.py` | Package marker |
| `tests/zotero_extract/test_config.py` | Config sanity tests |
| `tests/zotero_extract/test_org_writer.py` | Parsing and insertion tests |
| `tests/zotero_extract/test_zotero_client.py` | API client tests with mocked HTTP |

---

### Task 1: Project scaffolding

**Files:**
- Create: `scripts/zotero_extract/__init__.py`
- Create: `scripts/zotero_extract/requirements.txt`
- Create: `tests/zotero_extract/__init__.py`

- [ ] **Step 1: Create directories and marker files**

```bash
mkdir -p ~/Org/scripts/zotero_extract
mkdir -p ~/Org/tests/zotero_extract
touch ~/Org/scripts/zotero_extract/__init__.py
touch ~/Org/tests/zotero_extract/__init__.py
```

- [ ] **Step 2: Write requirements.txt**

File: `scripts/zotero_extract/requirements.txt`

```
requests>=2.31
pytest>=7.0
```

- [ ] **Step 3: Install dependencies**

```bash
cd ~/Org
pip install -r scripts/zotero_extract/requirements.txt
```

Expected: `Successfully installed requests-... pytest-...`

- [ ] **Step 4: Commit**

```bash
git -C ~/Org add scripts/zotero_extract/ tests/zotero_extract/
git -C ~/Org commit -m "chore: scaffold zotero extract project"
```

---

### Task 2: config.py — routing dictionaries

**Files:**
- Create: `scripts/zotero_extract/config.py`
- Create: `tests/zotero_extract/test_config.py`

- [ ] **Step 1: Write failing test**

File: `tests/zotero_extract/test_config.py`

```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from scripts.zotero_extract.config import CODETAG_TO_SECTION, FALLBACK_SECTION


def test_all_fish_sections_reachable():
    sections = set(CODETAG_TO_SECTION.values())
    expected = {
        "** Background and motivation",
        "** Supporting Ideas and hypothesis",
        "** Purpose, Relevance, and Contribution",
        "** Methodology",
        "** Results",
        "** Interesting findings and not categorized stuff",
        "** Critics",
    }
    assert expected.issubset(sections)


def test_codetags_are_lowercase():
    for key in CODETAG_TO_SECTION:
        assert key == key.lower(), f"Key '{key}' must be lowercase"


def test_fallback_is_findings():
    assert FALLBACK_SECTION == "** Interesting findings and not categorized stuff"
```

- [ ] **Step 2: Run to verify failure**

```bash
cd ~/Org && python -m pytest tests/zotero_extract/test_config.py -v
```

Expected: `ModuleNotFoundError` or `ImportError`

- [ ] **Step 3: Implement config.py**

File: `scripts/zotero_extract/config.py`

```python
CODETAG_TO_SECTION = {
    "background": "** Background and motivation",
    "support": "** Supporting Ideas and hypothesis",
    "supporting ideas": "** Supporting Ideas and hypothesis",
    "purpose": "** Purpose, Relevance, and Contribution",
    "contribution": "** Purpose, Relevance, and Contribution",
    "method": "** Methodology",
    "methodology": "** Methodology",
    "results": "** Results",
    "findings": "** Interesting findings and not categorized stuff",
    "critics": "** Critics",
    "critic": "** Critics",
}

FALLBACK_SECTION = "** Interesting findings and not categorized stuff"
ANNOTATIONS_SECTION = "* Annotations (zotero)"
UNCATEGORIZED_SECTION = "* Uncategorized annotations"
ZOTERO_BASE = "http://localhost:23119/api/users/0"
ORG_SEARCH_DIR = "~/Org"
```

- [ ] **Step 4: Run to verify passing**

```bash
cd ~/Org && python -m pytest tests/zotero_extract/test_config.py -v
```

Expected: `3 passed`

- [ ] **Step 5: Commit**

```bash
git -C ~/Org add scripts/zotero_extract/config.py tests/zotero_extract/test_config.py
git -C ~/Org commit -m "feat: add codetag-to-section routing config"
```

---

### Task 3: org_writer.py — codetag parsing and routing

**Files:**
- Create: `scripts/zotero_extract/org_writer.py` (parsing functions only)
- Create: `tests/zotero_extract/test_org_writer.py` (parsing tests)

- [ ] **Step 1: Write failing tests**

File: `tests/zotero_extract/test_org_writer.py`

```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

import pytest
from scripts.zotero_extract.org_writer import parse_codetag, route_comment
from scripts.zotero_extract.config import FALLBACK_SECTION


def test_parse_codetag_curly_braces():
    assert parse_codetag("{BACKGROUND} some text") == "background"


def test_parse_codetag_square_brackets():
    assert parse_codetag("[RESULTS]") == "results"


def test_parse_codetag_title_case():
    assert parse_codetag("{Method}") == "method"


def test_parse_codetag_multi_word():
    assert parse_codetag("[Supporting Ideas] text") == "supporting ideas"


def test_parse_codetag_returns_none_when_absent():
    assert parse_codetag("plain text no tag") is None


def test_route_comment_known_tag():
    assert route_comment("{METHOD} details") == "** Methodology"


def test_route_comment_unknown_tag_falls_back():
    assert route_comment("{UNKNOWN_TAG}") == FALLBACK_SECTION


def test_route_comment_no_tag_falls_back():
    assert route_comment("no tag here") == FALLBACK_SECTION
```

- [ ] **Step 2: Run to verify failure**

```bash
cd ~/Org && python -m pytest tests/zotero_extract/test_org_writer.py -v
```

Expected: `ImportError`

- [ ] **Step 3: Implement parsing functions**

File: `scripts/zotero_extract/org_writer.py`

```python
import re
import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
from config import CODETAG_TO_SECTION, FALLBACK_SECTION, ANNOTATIONS_SECTION, UNCATEGORIZED_SECTION


def parse_codetag(comment: str) -> str | None:
    match = re.search(r'[\{\[]([^\}\]]+)[\}\]]', comment)
    if match:
        return match.group(1).strip().lower()
    return None


def route_comment(comment: str) -> str:
    tag = parse_codetag(comment)
    if tag:
        return CODETAG_TO_SECTION.get(tag, FALLBACK_SECTION)
    return FALLBACK_SECTION
```

- [ ] **Step 4: Run to verify passing**

```bash
cd ~/Org && python -m pytest tests/zotero_extract/test_org_writer.py -v
```

Expected: `8 passed`

- [ ] **Step 5: Commit**

```bash
git -C ~/Org add scripts/zotero_extract/org_writer.py tests/zotero_extract/test_org_writer.py
git -C ~/Org commit -m "feat: implement codetag parsing and section routing"
```

---

### Task 4: org_writer.py — file search and idempotency

**Files:**
- Modify: `scripts/zotero_extract/org_writer.py`
- Modify: `tests/zotero_extract/test_org_writer.py`

- [ ] **Step 1: Write failing tests**

Append to `tests/zotero_extract/test_org_writer.py` (also add import at top: `from scripts.zotero_extract.org_writer import parse_codetag, route_comment, find_org_file, already_inserted`):

```python
from scripts.zotero_extract.org_writer import find_org_file, already_inserted


def test_find_org_file_by_reference(tmp_path):
    org = tmp_path / "paper.org"
    org.write_text("#+title: Test\n#+reference: minsky_1977\n\nContent\n")
    assert find_org_file("minsky_1977", tmp_path) == org


def test_find_org_file_raises_when_not_found(tmp_path):
    with pytest.raises(FileNotFoundError):
        find_org_file("nonexistent_key", tmp_path)


def test_already_inserted_true():
    assert already_inserted("Some text [zotero:K3XP9D]\nMore", "K3XP9D") is True


def test_already_inserted_false():
    assert already_inserted("Some text\nMore", "K3XP9D") is False
```

- [ ] **Step 2: Run to verify failure**

```bash
cd ~/Org && python -m pytest tests/zotero_extract/test_org_writer.py::test_find_org_file_by_reference -v
```

Expected: `ImportError`

- [ ] **Step 3: Implement file search and idempotency check**

Append to `scripts/zotero_extract/org_writer.py`:

```python
def find_org_file(citekey: str, search_dir: Path) -> Path:
    for path in sorted(search_dir.rglob("*.org")):
        text = path.read_text(encoding="utf-8")
        if re.search(rf'^#\+reference:\s+{re.escape(citekey)}\s*$', text, re.MULTILINE):
            return path
    raise FileNotFoundError(f"No .org file found for citekey: {citekey}")


def already_inserted(content: str, annotation_key: str) -> bool:
    return f"[zotero:{annotation_key}]" in content
```

- [ ] **Step 4: Run to verify passing**

```bash
cd ~/Org && python -m pytest tests/zotero_extract/test_org_writer.py -v
```

Expected: `12 passed`

- [ ] **Step 5: Commit**

```bash
git -C ~/Org add scripts/zotero_extract/org_writer.py tests/zotero_extract/test_org_writer.py
git -C ~/Org commit -m "feat: add org file search by citekey and idempotency check"
```

---

### Task 5: org_writer.py — section insertion

**Files:**
- Modify: `scripts/zotero_extract/org_writer.py`
- Modify: `tests/zotero_extract/test_org_writer.py`

- [ ] **Step 1: Write failing tests**

Append to `tests/zotero_extract/test_org_writer.py` (also add import: `from scripts.zotero_extract.org_writer import insert_annotations`):

```python
from scripts.zotero_extract.org_writer import insert_annotations

ORG_CONTENT = """\
* FISH-5SS

** Background and motivation

** Methodology

** Results

** Interesting findings and not categorized stuff

** Critics

* Annotations (zotero)

* Additional Backlinks
"""


def test_insert_comment_into_correct_section(tmp_path):
    f = tmp_path / "paper.org"
    f.write_text(ORG_CONTENT)
    annotations = [
        {"key": "AA1", "annotationComment": "{BACKGROUND} Keynes context",
         "annotationText": "", "annotationPageLabel": "1"}
    ]
    insert_annotations(f, annotations)
    content = f.read_text()
    assert "- Keynes context [zotero:AA1]" in content
    assert content.index("** Background and motivation") < content.index("- Keynes context [zotero:AA1]")


def test_insert_highlight_into_annotations_section(tmp_path):
    f = tmp_path / "paper.org"
    f.write_text(ORG_CONTENT)
    annotations = [
        {"key": "BB2", "annotationComment": "",
         "annotationText": "Financial instability is endogenous.", "annotationPageLabel": "5"}
    ]
    insert_annotations(f, annotations)
    content = f.read_text()
    assert "- [p. 5] Financial instability is endogenous. [zotero:BB2]" in content
    assert content.index("* Annotations (zotero)") < content.index("- [p. 5]")


def test_annotation_with_both_comment_and_text(tmp_path):
    f = tmp_path / "paper.org"
    f.write_text(ORG_CONTENT)
    annotations = [
        {"key": "CC3", "annotationComment": "{RESULTS} Key finding",
         "annotationText": "Stability is cyclical.", "annotationPageLabel": "8"}
    ]
    insert_annotations(f, annotations)
    content = f.read_text()
    assert "- Key finding [zotero:CC3]" in content
    assert "- [p. 8] Stability is cyclical. [zotero:CC3]" in content


def test_idempotency(tmp_path):
    f = tmp_path / "paper.org"
    f.write_text(ORG_CONTENT)
    annotations = [
        {"key": "DD4", "annotationComment": "{RESULTS} Key result",
         "annotationText": "", "annotationPageLabel": "7"}
    ]
    insert_annotations(f, annotations)
    insert_annotations(f, annotations)
    assert f.read_text().count("[zotero:DD4]") == 1


def test_missing_section_goes_to_uncategorized(tmp_path):
    f = tmp_path / "paper.org"
    # File with no Critics section
    f.write_text("* FISH-5SS\n\n* Annotations (zotero)\n")
    annotations = [
        {"key": "EE5", "annotationComment": "{CRITICS} A critique",
         "annotationText": "", "annotationPageLabel": "2"}
    ]
    insert_annotations(f, annotations)
    content = f.read_text()
    assert "* Uncategorized annotations" in content
    assert "[zotero:EE5]" in content
```

- [ ] **Step 2: Run to verify failure**

```bash
cd ~/Org && python -m pytest tests/zotero_extract/test_org_writer.py::test_insert_comment_into_correct_section -v
```

Expected: `ImportError` for `insert_annotations`

- [ ] **Step 3: Implement insert_annotations**

Append to `scripts/zotero_extract/org_writer.py`:

```python
def _heading_level(line: str) -> int | None:
    m = re.match(r'^(\*+)\s', line)
    return len(m.group(1)) if m else None


def _find_insertion_index(lines: list[str], heading: str) -> int | None:
    """Return index to insert after (end of section), or None if heading not found."""
    heading_stripped = heading.strip()
    for i, line in enumerate(lines):
        if line.strip() == heading_stripped:
            level = _heading_level(line)
            j = i + 1
            while j < len(lines):
                lvl = _heading_level(lines[j])
                if lvl is not None and lvl <= level:
                    break
                j += 1
            # Insert before trailing blank lines
            while j > i + 1 and not lines[j - 1].strip():
                j -= 1
            return j
    return None


def insert_annotations(file_path: Path, annotations: list[dict]) -> None:
    content = file_path.read_text(encoding="utf-8")
    lines = content.splitlines(keepends=True)

    for ann in annotations:
        key = ann["key"]
        if already_inserted("".join(lines), key):
            continue

        comment = ann.get("annotationComment", "").strip()
        text = ann.get("annotationText", "").strip()
        page = ann.get("annotationPageLabel", "?")

        if comment:
            clean = re.sub(r'[\{\[][^\}\]]+[\}\]]\s*', '', comment).strip()
            entry = f"- {clean} [zotero:{key}]\n"
            target = route_comment(comment)
            idx = _find_insertion_index(lines, target)
            if idx is not None:
                lines.insert(idx, entry)
            else:
                lines = _append_uncategorized(lines, entry)

        if text:
            entry = f"- [p. {page}] {text} [zotero:{key}]\n"
            idx = _find_insertion_index(lines, ANNOTATIONS_SECTION)
            if idx is not None:
                lines.insert(idx, entry)
            else:
                lines = _append_uncategorized(lines, entry)

    file_path.write_text("".join(lines), encoding="utf-8")


def _append_uncategorized(lines: list[str], entry: str) -> list[str]:
    heading = f"{UNCATEGORIZED_SECTION}\n"
    for i, line in enumerate(lines):
        if line.strip() == UNCATEGORIZED_SECTION.strip():
            lines.insert(i + 1, entry)
            return lines
    lines.append(f"\n{heading}{entry}")
    return lines
```

- [ ] **Step 4: Run to verify passing**

```bash
cd ~/Org && python -m pytest tests/zotero_extract/test_org_writer.py -v
```

Expected: `17 passed`

- [ ] **Step 5: Commit**

```bash
git -C ~/Org add scripts/zotero_extract/org_writer.py tests/zotero_extract/test_org_writer.py
git -C ~/Org commit -m "feat: implement annotation insertion into org sections"
```

---

### Task 6: zotero_client.py — Zotero local API

**Files:**
- Create: `scripts/zotero_extract/zotero_client.py`
- Create: `tests/zotero_extract/test_zotero_client.py`

Zotero local API base: `http://localhost:23119/api/users/0`. No auth needed for local access. Annotations are child items of the PDF attachment with `itemType == "annotation"`. Better BibTeX stores the citekey in the `extra` field as `Citation Key: <citekey>`.

- [ ] **Step 1: Write failing tests**

File: `tests/zotero_extract/test_zotero_client.py`

```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

import pytest
from unittest.mock import patch, Mock
from scripts.zotero_extract.zotero_client import get_item_key, get_pdf_key, get_annotations

MOCK_ITEMS = [
    {"key": "ABCD1234", "data": {"key": "ABCD1234", "extra": "Citation Key: minsky_1977_Financial\nDOI: 10.1/x", "itemType": "journalArticle"}},
    {"key": "ZZZZ9999", "data": {"key": "ZZZZ9999", "extra": "Citation Key: other_2020", "itemType": "journalArticle"}},
]

MOCK_CHILDREN_PARENT = [
    {"key": "PDF00001", "data": {"key": "PDF00001", "contentType": "application/pdf", "itemType": "attachment"}},
    {"key": "NOTE0001", "data": {"key": "NOTE0001", "contentType": "", "itemType": "note"}},
]

MOCK_CHILDREN_PDF = [
    {"key": "ANN00001", "data": {"key": "ANN00001", "itemType": "annotation", "annotationType": "highlight",
                                  "annotationText": "some text", "annotationComment": "{BACKGROUND}",
                                  "annotationPageLabel": "3", "annotationColor": "#ffd400"}},
    {"key": "NOTE0002", "data": {"key": "NOTE0002", "itemType": "note"}},
]


def make_mock_get(url, params=None):
    r = Mock()
    r.raise_for_status = Mock()
    if "PDF00001/children" in url:
        r.json.return_value = MOCK_CHILDREN_PDF
    elif "/children" in url:
        r.json.return_value = MOCK_CHILDREN_PARENT
    else:
        r.json.return_value = MOCK_ITEMS
    return r


@patch("scripts.zotero_extract.zotero_client.requests.get", side_effect=make_mock_get)
def test_get_item_key_finds_by_citekey(_):
    assert get_item_key("minsky_1977_Financial") == "ABCD1234"


@patch("scripts.zotero_extract.zotero_client.requests.get", side_effect=make_mock_get)
def test_get_item_key_raises_when_not_found(_):
    with pytest.raises(ValueError, match="No Zotero item"):
        get_item_key("missing_2099")


@patch("scripts.zotero_extract.zotero_client.requests.get", side_effect=make_mock_get)
def test_get_pdf_key_returns_pdf_attachment(_):
    assert get_pdf_key("ABCD1234") == "PDF00001"


@patch("scripts.zotero_extract.zotero_client.requests.get", side_effect=make_mock_get)
def test_get_annotations_returns_only_annotation_items(_):
    anns = get_annotations("PDF00001")
    assert len(anns) == 1
    assert anns[0]["annotationType"] == "highlight"
    assert anns[0]["key"] == "ANN00001"
```

- [ ] **Step 2: Run to verify failure**

```bash
cd ~/Org && python -m pytest tests/zotero_extract/test_zotero_client.py -v
```

Expected: `ImportError`

- [ ] **Step 3: Implement zotero_client.py**

File: `scripts/zotero_extract/zotero_client.py`

```python
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import requests
from config import ZOTERO_BASE


def get_item_key(citekey: str) -> str:
    resp = requests.get(f"{ZOTERO_BASE}/items", params={"q": citekey, "format": "json", "limit": 100})
    resp.raise_for_status()
    for item in resp.json():
        extra = item.get("data", {}).get("extra", "")
        if f"Citation Key: {citekey}" in extra:
            return item["key"]
    raise ValueError(f"No Zotero item found for citekey: {citekey}")


def get_pdf_key(item_key: str) -> str:
    resp = requests.get(f"{ZOTERO_BASE}/items/{item_key}/children", params={"format": "json"})
    resp.raise_for_status()
    for child in resp.json():
        if child.get("data", {}).get("contentType") == "application/pdf":
            return child["key"]
    raise ValueError(f"No PDF attachment found for item: {item_key}")


def get_annotations(pdf_key: str) -> list[dict]:
    resp = requests.get(f"{ZOTERO_BASE}/items/{pdf_key}/children", params={"format": "json"})
    resp.raise_for_status()
    return [
        item["data"]
        for item in resp.json()
        if item.get("data", {}).get("itemType") == "annotation"
    ]
```

- [ ] **Step 4: Run to verify passing**

```bash
cd ~/Org && python -m pytest tests/zotero_extract/test_zotero_client.py -v
```

Expected: `4 passed`

- [ ] **Step 5: Commit**

```bash
git -C ~/Org add scripts/zotero_extract/zotero_client.py tests/zotero_extract/test_zotero_client.py
git -C ~/Org commit -m "feat: implement Zotero local API client"
```

---

### Task 7: extract_zotero.py — CLI entry point

**Files:**
- Create: `scripts/zotero_extract/extract_zotero.py`

- [ ] **Step 1: Implement CLI**

File: `scripts/zotero_extract/extract_zotero.py`

```python
import argparse
import sys
from pathlib import Path
import requests

sys.path.insert(0, str(Path(__file__).parent))
from config import ORG_SEARCH_DIR
from zotero_client import get_item_key, get_pdf_key, get_annotations
from org_writer import find_org_file, insert_annotations


def main():
    parser = argparse.ArgumentParser(
        description="Extract Zotero annotations into Org bib file"
    )
    parser.add_argument("citekey", help="Better BibTeX citation key (used for Zotero lookup)")
    parser.add_argument("--file", type=Path, help="Path to .org file (skips automatic search)")
    args = parser.parse_args()

    try:
        item_key = get_item_key(args.citekey)
        pdf_key = get_pdf_key(item_key)
        annotations = get_annotations(pdf_key)
    except requests.ConnectionError:
        print("Error: Cannot connect to Zotero. Make sure Zotero is open.", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        org_file = args.file if args.file else find_org_file(
            args.citekey, Path(ORG_SEARCH_DIR).expanduser()
        )
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    insert_annotations(org_file, annotations)
    print(f"Done: {len(annotations)} annotation(s) processed → {org_file}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run full test suite**

```bash
cd ~/Org && python -m pytest tests/zotero_extract/ -v
```

Expected: all tests pass (25 total)

- [ ] **Step 3: Smoke test (requires Zotero open with a known paper)**

```bash
cd ~/Org/scripts/zotero_extract
python extract_zotero.py minsky_1977_Financial
```

Expected: `Done: N annotation(s) processed → /home/gpetrini/Org/...bib.org`

If Zotero is closed: `Error: Cannot connect to Zotero. Make sure Zotero is open.`

With explicit file:
```bash
python extract_zotero.py minsky_1977_Financial --file ~/Org/20201204T000000--the-financial-instability-hypothesis-an-interpretation-of-keynes-and-an-alternative-to-standard-theory__bib.org
```

- [ ] **Step 4: Commit**

```bash
git -C ~/Org add scripts/zotero_extract/extract_zotero.py
git -C ~/Org commit -m "feat: add CLI entry point for zotero annotation extractor"
```

---

## Notes for execution

- **Zotero local API port:** `localhost:23119` — enabled by default in Zotero 6+. If connection fails, check Zotero → Edit → Preferences → Advanced → Allow other applications on this computer to communicate with Zotero.
- **Better BibTeX required:** The citekey lookup relies on BBT storing `Citation Key: <citekey>` in the `extra` field. If BBT is not installed, `get_item_key` will always raise `ValueError`.
- **Large libraries:** `get_item_key` fetches up to 100 results matching the query. If the citekey is not found, increase the `limit` parameter or add pagination.
- **Annotation `key` field:** The Zotero local API returns annotation data with `key` inside `data`. The `insert_annotations` function reads `ann["key"]` — this matches what `get_annotations` returns.
