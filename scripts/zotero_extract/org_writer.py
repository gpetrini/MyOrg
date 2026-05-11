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


def find_org_file(citekey: str, search_dir: Path) -> Path:
    for path in sorted(search_dir.rglob("*.org")):
        text = path.read_text(encoding="utf-8")
        if re.search(rf'^#\+reference:\s+{re.escape(citekey)}\s*$', text, re.MULTILINE):
            return path
    raise FileNotFoundError(f"No .org file found for citekey: {citekey}")


def already_inserted(content: str, annotation_key: str) -> bool:
    return f"[zotero:{annotation_key}]" in content


def _heading_level(line: str) -> int | None:
    m = re.match(r'^(\*+)\s', line)
    return len(m.group(1)) if m else None


def _find_insertion_index(lines: list[str], heading: str) -> int | None:
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
